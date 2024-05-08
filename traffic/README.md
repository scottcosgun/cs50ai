I especially enjoyed coding traffic.py due the the exploration of documentation and stackoverflow that was required to implement the program. This project involved many modules (os, cv2, tensorflow, numpy, etc.) that I had not used in previous projects, which greatly expanded my knowledge of these modules. 
In creating the neural network, I created convolutional layers of 32 and 64 neurons using 3x3 kernels and relu activation. I created 3 pooling layers, using max pooling with a 2x2 pool size to reduce image sizes. With each step, I also dropped 10% of neurons to help combat overfitting.
I noticed that with two iterations of convolution, max_pooling, and dropout, each epoch took approximately 15s (30ms/step), with a final loss of 0.1422, accuracy of 0.9634, with 4s/epoch and 12ms/step.
When adding an additional ideration of convolution with 64 neurons, max pooling, and dropout, the time for each epoch was slightly longer (16 - 20s 32 - 40ms/step), however the final loss and accuracy were slightly improved at a loss of 0.0934 and accuracy of 0.9755. Notably, the time at this last step was much improved, with 2s/epoch - 7ms/step.