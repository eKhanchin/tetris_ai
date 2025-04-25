import os
import numpy as np
import pickle
import threading
from enum import Enum, auto
from PyQt5.QtCore import QThread, pyqtSignal

from model.brain import Brain
from model.dqn import DQN


class ProcessType(Enum):
    TRAINING = auto()
    PLAYING = auto()


class ModelThread(QThread):
    """ An AI model that runs on a thread.

    Args:
        QThread (_type_): _description_

    Returns:
        _type_: _description_
    """
    
    reset = pyqtSignal()
    step = pyqtSignal(int)

    def __init__(self, env_height: int, env_width: int, process_type: ProcessType):
        super().__init__()

        self.env_height = env_height
        self.env_width = env_width
        self.process_type = process_type
        
        # # Hyper parameters
        self.learning_rate = 0.00001
        self.max_memory = 100_000
        self.gamma = 0.9  # More importance to future rewards
        self.batch_size = 16
        self.last_states_number = 4
        self.epsilon = 1.0  # Exploration - default: 1.0
        self.epsilon_decay = 0.0002  # Exploitation
        self.epsilon_min = 0.05 
        self.epochs_number = 0

        self.model_file_path = 'model.keras'
        self.memory_file_path = 'model_memory'
        self.memory_file_path_temp = "model_memory.temp"

        self.dqn = None
        self.model = None
        self.frame = None
        self.reward = 0
        self.game_over = False
        
        self.event = threading.Event()
        
        self._set_model()

    def _set_model(self):
        # Selects brain object
        if self.process_type == ProcessType.TRAINING:
            brain = Brain(
                (self.env_height, self.env_width, self.last_states_number),
                self.learning_rate
            )
        else:
            brain = Brain((self.env_height, self.env_width,
                           self.last_states_number))
            
        self.dqn = DQN(self.max_memory, self.gamma)
        
        # Loads existing model or create a new one.
        if os.path.isfile(self.model_file_path):
            self.model = self._load_model(brain)
                
            print((f'Loaded existing model with epsilon: {self.epsilon:.5f},'
                f' memory slots: {len(self.dqn.memory)}, epochs: {self.epochs_number}'))
        else:
            self.model = brain.create_model()
            print('Created new model')
    
    def _load_model(self, brain: Brain):
        epsilon = 0
        epochs_number = 0
        
        model = brain.load_model(self.model_file_path)
        if os.path.isfile(self.memory_file_path):
            with open(self.memory_file_path, 'rb') as file:
                self.dqn.memory, epsilon, epochs_number = pickle.load(file)

        if epsilon > 0:
            self.epsilon = epsilon
        
        if epochs_number > 0:
            self.epochs_number = epochs_number
        
        return model
    
    def _reset_states(self):
        """ Resets the states.
        
        Takes a random state as current and as a next state.
        """
        
        batch_size = 1
        current_state = np.zeros((
            batch_size, self.env_height, self.env_width, self.last_states_number))
        
        for i in range(self.last_states_number):
            current_state[0, :, :, i] = self.frame  # Takes 4 last frames
        
        return current_state, current_state

    def _get_current_state(self):
        return self.frame, self.reward, self.game_over
    
    def _save_progress(self):
        self.model.save(self.model_file_path)
        
        with open(self.memory_file_path_temp, 'wb') as file:
            # First writes into the temp file to prevent corruption of the
            # original file
            pickle.dump([self.dqn.memory, self.epsilon, self.epochs_number], file)
        os.replace(self.memory_file_path_temp, self.memory_file_path)
    
    def _train(self):
        self.epochs_number += 1
            
        self.reset.emit()
        self.event.wait()  # Block until the event is set
        self.event.clear()  # Clear the event for the next cycle
        
        current_state, next_state = self._reset_states()
        
        game_over = False
        steps = 0
        while not game_over:
            steps += 1
            
            # Select action
            if np.random.rand() <= self.epsilon:
                # Exploration
                action = np.random.randint(0, 4)
            else:
                # Exploitation
                q_values = self.model.predict(current_state, verbose=0)[0]  # First action
                action = int(np.argmax(q_values))
            
            # Update the environment
            self.step.emit(action)
            self.event.wait()  # Block until the event is set
            self.event.clear()  # Clear the event for the next cycle
            
            frame, reward, game_over = self._get_current_state()
            
            frame = np.reshape(frame, (1, self.env_height, self.env_width, 1))
            
            # axis=3 is a number of frames. Here we add new frame to the
            # next state
            next_state = np.append(next_state, frame, axis=3)
            
            # Previous state should be removed, the oldest one
            next_state = np.delete(next_state, 0, axis=3)
            
            self.dqn.remember([current_state, action, reward, next_state], game_over)
            inputs, targets = self.dqn.get_batch(self.model, self.batch_size)
            # TODO: Consider checking inputs and targets types
            
            self.model.train_on_batch(inputs, targets)
                                                    
        # Update epsilon and save the model
        self.epsilon -= self.epsilon_decay
        self.epsilon = max(self.epsilon, self.epsilon_min)
        
        self._save_progress()
        
        print(
            (f'Epoch {self.epochs_number} - current score: {reward},'
            f' epsilon: {self.epsilon:.5f},'
            f' memory slots: {len(self.dqn.memory)}, steps: {steps}')
        )
    
    def _play(self):
        self.reset.emit()
        self.event.wait()  # Block until the event is set
        self.event.clear()  # Clear the event for the next cycle
        
        current_state, next_state = self._reset_states()
        game_over = False
        while not game_over:
            q_values = self.model.predict(current_state, verbose=0)[0]
            action = int(np.argmax(q_values))
            
            self.step.emit(action)
            self.event.wait()  # Block until the event is set
            self.event.clear()  # Clear the event for the next cycle
            
            frame, _, game_over = self._get_current_state()
            
            frame = np.reshape(frame, (1, self.env_height, self.env_width, 1))
            
            # axis=3 is a number of frames. Here we add new frame to the
            # next state
            next_state = np.append(next_state, frame, axis=3)
            
            # Previous state should be removed, the oldest one
            next_state = np.delete(next_state, 0, axis=3)
            
            current_state = next_state

    def receive_state(self, current_state: tuple):
        """ Receives signal from the Tetris GUI of current state.

        Args:
            current_state (tuple): A tuple that describes current board
                state, reward score and game over state.
        """
        self.frame, self.reward, self.game_over = current_state
        self.event.set()
    
    def run(self):
        """ Main function that runs when the thread starts. """
        
        if self.process_type == ProcessType.TRAINING:
            process_function = self._train
        else:
            process_function = self._play
        
        while True:
            process_function()
