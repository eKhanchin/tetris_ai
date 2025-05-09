import numpy as np
import os
import pickle

from main.actions import Action
from main.game_manager import GameManager
from model.brain import Brain
from model.dqn import DQN


# TODO: Put hyperparameters into a file - TOML or JSON.
# Hyper parameters
LEARNING_RATE = 0.00001
MAX_MEMORY = 100_000
GAMMA = 0.9  # More importance to future rewards
BATCH_SIZE = 16
LAST_STATES_NUMBER = 4
epsilon = 1.0  # Exploration - default: 1.0
EPSILON_DECAY = 0.0002  # Exploitation
EPSILON_MIN = 0.05 

MODEL_FILE_PATH = 'model.keras'
MEMORY_FILE_PATH = 'model_memory'
MEMORY_FILE_PATH_TEMP = "model_memory.temp"


env = GameManager()
HEIGHT = env.board_height
WIDTH = env.board_width

brain = Brain((HEIGHT, WIDTH, LAST_STATES_NUMBER), LEARNING_RATE)
dqn = DQN(MAX_MEMORY, GAMMA)
epochs_number = 0
ACTIONS = list(Action)

        
# Loads existing model or create a new one.
if os.path.isfile(MODEL_FILE_PATH):
    model = brain.load_model(MODEL_FILE_PATH)
    if os.path.isfile(MEMORY_FILE_PATH):
        with open(MEMORY_FILE_PATH, 'rb') as file:
            dqn.memory, epsilon, epochs_number = pickle.load(file)

    print((f'Loaded existing model with epsilon: {epsilon:.5f},'
           f' memory slots: {len(dqn.memory)}, epochs: {epochs_number}'))
else:
    model = brain.create_model()
    print('Created new model')


def reset_states():
    """ Resets the states.
    
    Takes a random state as current and as a next state.
    """
    
    batch_size = 1
    state = np.zeros((batch_size, HEIGHT, WIDTH, LAST_STATES_NUMBER))
    
    for i in range(LAST_STATES_NUMBER):
        state[0, :, :, i] = env.board  # Takes 4 last frames
    
    return state, state


# Game loop
while True:
    epochs_number += 1
    env.reset()
    current_state, next_state = reset_states()
    
    game_over = False
    steps = 0
    while not game_over:
        steps += 1
        
        # Select action
        if np.random.rand() <= epsilon:
            # Exploration
            action = np.random.randint(0, 4)
        else:
            # Exploitation
            q_values = model.predict(current_state, verbose=0)[0]  # First action
            action = int(np.argmax(q_values))

        # Update the environment
        frame, reward, game_over = env.step(action)
        
        frame = np.reshape(frame, (1, HEIGHT, WIDTH, 1))
        # axis=3 is a number of frames. Here we add new frame to the
        # next state
        next_state = np.append(next_state, frame, axis=3)
        
        # Previous state should be removed, the oldest one
        next_state = np.delete(next_state, 0, axis=3)
        
        dqn.remember([current_state, action, reward, next_state], game_over)
        inputs, targets = dqn.get_batch(model, BATCH_SIZE)
        
        model.train_on_batch(inputs, targets)
        
        current_state = next_state
                
    # Update epsilon and save the model
    epsilon -= EPSILON_DECAY
    epsilon = max(epsilon, EPSILON_MIN)
        
    model.save(MODEL_FILE_PATH)
    with open(MEMORY_FILE_PATH_TEMP, 'wb') as file:
        # First writes into the temp file to prevent corruption of the
        # original file
        pickle.dump([dqn.memory, epsilon, epochs_number], file)
    os.replace(MEMORY_FILE_PATH_TEMP, MEMORY_FILE_PATH)
    
    print((
        f'Epoch {epochs_number} - current score: {reward},'
        f' epsilon: {epsilon:.5f}, memory slots: {len(dqn.memory)}, steps: {steps}'
    ))
        