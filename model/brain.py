from keras.models import Sequential, load_model
from keras.layers import Conv2D, MaxPooling2D, Flatten, Dense
from keras.optimizers import Adam


class Brain:
    """ Resembles model's brain. """
    def __init__(self, input_shape, learning_rate=0.005):
        self.input_shape = input_shape
        self.learning_rate = learning_rate
        self.outputs_number = 4   
    
    def create_model(self):
        """ Creates a sequential CNN model. """
        model = Sequential()
        
        # CNN part
        # Convolution neural network alone cannot give us prediction.
        # So on top of that we'll need artificial neural network (ANN),
        # because we need prediction and the output layer.
        #
        # Here 32 neurons are 32 filters to extract features. (3, 3) means
        # the size of filters.
        model.add(Conv2D(32, (3, 3), activation='relu',
                              input_shape=self.input_shape))  # Input layer
        model.add(MaxPooling2D((2, 2)))
        model.add(Conv2D(64, (2, 2), activation='relu'))
        
        model.add(Flatten())  # Needed to connect CNN and ANN
        
        # Fully connected neural network, ANN part
        model.add(Dense(256, activation='relu'))
        model.add(Dense(self.outputs_number))  # Output layer
        
        model.compile(optimizer=Adam(learning_rate=self.learning_rate), loss='mse')
        
        return model
        
    def load_model(self, file_path):
        """ Loads model from a given file path."""
        
        return load_model(file_path)
