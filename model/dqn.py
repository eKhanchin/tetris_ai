import numpy as np


class DQN:
    def __init__(self, max_memory, gamma):
        self.max_memory = max_memory
        self.gamma = gamma
        
        # Experiences (state, action, reward, next_state, game_over)
        self.memory = []
    
    def remember(self, transition, game_over):
        """ Remembers new experience.

        Args:
            transition: From current to next state, action and a reward.
            game_over: Game's state.
        """
        
        self.memory.append([transition, game_over])
        if len(self.memory) > self.max_memory:
            del self.memory[0]  # Oldest experience
    
    def get_batch(self, model, batch_size):
        """ Get batches of input/output. Training data. """
        
        outputs_number = model.output_shape[-1]
        min_batch_size = min(batch_size, len(self.memory))
        
        # Initialization of input/targets
        # Exploration
        #
        # First experience -> transition -> state -> shape's height
        # shape[1] - because Keras input is always a column
        state_height = self.memory[0][0][0].shape[1]
        state_width = self.memory[0][0][0].shape[2]
        frames_number = self.memory[0][0][0].shape[3]  # For convolution network
        inputs = np.zeros((
            min_batch_size, state_height, state_width, frames_number
        ))
        
        targets = np.zeros((min_batch_size, outputs_number))
        
        # Extract experience randomly
        for i, t_index in enumerate(np.random.randint(
                0, len(self.memory), size=min_batch_size)):
            current_state, action, reward, next_state = self.memory[t_index][0]
            game_over = self.memory[t_index][1]
            
            # Update inputs and targets
            inputs[i] = current_state
            targets[i] = model.predict(current_state, verbose=0)[0]  # Picks the highest probability
            
            # Q-Learning update rule
            if game_over:
                targets[i][action] = reward
            else:
                targets[i][action] = (reward + self.gamma
                                      * np.max(model.predict(next_state, verbose=0)[0]))
            
        return inputs, targets
