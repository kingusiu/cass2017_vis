# ==============================================================================
# Copyright 2017 Hamid Younesy. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
import numpy as np
import matplotlib.pyplot as plt
#import matplotlib
from matplotlib import colors
from dataset import DataSet
from nn import Classifier
import random
import os

class Run:
    """
    A single run
    """
    num_samples = 200 # always fixed
    range_noise = [0.0, 0.5]
    range_training_ratio = [0.1, 0.9]
    range_batch_size = [1, 30]
    learning_rates = [0.00001, 0.0001, 0.001, 0.003, 0.01, 0.03, 0.1, 0.3, 1.0, 3.0, 10.0]
    regularization_rates = [0.0, 0.001, 0.003, 0.01, 0.03, 0.1, 0.3, 1.0, 3.0, 10.0]
    range_hidden = [0, 6]
    range_hidden_neuron = [1, 8]

    MODE_FULL = 'full'  # a single directory, with randomized data for each run
    MODE_PSA_RUNS = 'psa_runs'  # a few randomized data, in separate directories


    def __init__(self):
        # dataset parameters
        #self.dataset_name = DataSet.DATA_CIRCLE
        #self.noise = 0.0
        self.training_ratio = 0.5
        # classifier parameters
        self.batch_size = 10
        self.learning_rate = 0.3
        self.num_hidden = 2
        self.num_hidden_neuron = 3
        self.activation_h = Classifier.ACTIVATION_TANH  # activaion function for hidden layers
        self.regularization_type = Classifier.REGULARIZATION_NONE
        self.regularization_rate = 0.0

        self.data = None
        self.classifier = None

    def randomize_data(self, dataset_name=None, noise=None):
        # dataset parameters
        dataset_name = random.choice(DataSet.data_names) if dataset_name is None else dataset_name
        noise = random.uniform(*self.range_noise) if noise is None else noise
        self.data = DataSet(dataset_name, self.num_samples, noise)

    def randomize_training_params(self):
        # classifier parameters
        self.classifier = Classifier()
        self.classifier.training_ratio = random.uniform(*self.range_training_ratio)
        self.classifier.batch_size = random.randint(*self.range_batch_size)
        self.classifier.learning_rate = random.choice(self.learning_rates)
        self.classifier.num_hidden = random.randint(*self.range_hidden)
        self.classifier.num_hidden_neuron = random.randint(*self.range_hidden_neuron) if self.num_hidden > 0 else 0
        self.classifier.activation_h = random.choice(Classifier.activations_names)
        self.classifier.regularization_type = random.choice(Classifier.regularization_names)
        self.classifier.regularization_rate = random.choice(self.regularization_rates)
        self.classifier.build()

    def param_str(self):
        return "\t".join([self.data.dataset_name,
                          '{:0.2f}'.format(self.data.noise),
                          str(self.classifier.batch_size),
                          str(self.classifier.learning_rate),
                          str(self.classifier.num_hidden),
                          str(self.classifier.num_hidden_neuron),
                          self.classifier.activation_h,
                          self.classifier.regularization_type,
                          str(self.classifier.regularization_rate)
                          ])

    def param_names(self):
        return ['dataset','noise', 'batch_size', 'learning_rate', 'hidden_layers', 'neurons', 'activation', 'regularization', 'regularization_rate']

    def save_plot(self, filename):
        """
        Generates the plot using the current data and training state
        :param filename: output filename
        :return: None
        """
        # matplotlib.interactive(False)
        # plot the resulting classifier
        colormap = colors.ListedColormap(["#f59322", "#e8eaeb", "#0877bd"])
        x_min, x_max = -6, 6  # data.points[:, 0].min() - 1, data.points[:, 0].max() + 1
        y_min, y_max = -6, 6  # data.points[:, 1].min() - 1, data.points[:, 1].max() + 1
        xx, yy = np.meshgrid(np.linspace(x_min, x_max, 300),
                             np.linspace(y_min, y_max, 300))
        z = self.classifier.predict_y(np.c_[xx.ravel(), yy.ravel()]).reshape(xx.shape)
        fig = plt.figure(figsize=(4, 4), dpi=75)
        # plt.imshow(z, cmap=colormap, interpolation='nearest')
        plt.contourf(xx, yy, z, cmap=colormap, alpha=0.8)
        point_color = self.data.labels
        plt.scatter(self.data.points[:, 0], self.data.points[:, 1], c=point_color, s=30, cmap=colormap)
        plt.xlim(x_min, x_max)
        plt.ylim(y_min, y_max)
        fig.savefig(filename)
        plt.close()

    @staticmethod
    def create_dir(dirname):
        if not os.path.exists(dirname):
            os.makedirs(dirname)

    def execute_runs(self, mode, num_runs):
        """
        Executes several training runs, each with different parameters and saves the results
        :param mode: experiment mode.
            MODE_FULL randomizes all parameters including the input data, per run
            MODE_PSA_RUNS generates different datasets and runs the psa separately for each
        :param num_runs: number of runs per experiment
        :return:
        """

        iter_index = -1
        while True:
            iter_index += 1
            if mode == self.MODE_FULL:
                if iter_index == 1:
                    break
                out_dir = '../output/full'
                self.create_dir(out_dir)
                curr_data = None
            elif mode == self.MODE_PSA_RUNS:
                if iter_index >= len(DataSet.data_names):
                    break
                noise = 0.25
                dataset_name = DataSet.data_names[iter_index]
                out_dir = '../output/' + dataset_name + '_25'
                self.create_dir(out_dir)
                curr_data = DataSet(dataset_name, num_samples=Run.num_samples, noise=noise)
                curr_data.save_to_file(out_dir + '/input.txt')
            else:
                print("Invalid mode:" + str(mode))
                return

            # create write the header for the runs.txt file
            f_runs = open(out_dir + '/runs.txt', 'w')
            f_runs.write('\t'.join(['ID', 'imagePath']) + '\t' +
                         '\t'.join(self.param_names()) + '\t' +
                         '\t'.join(['step', 'train_loss', 'test_loss']) +
                         '\n')

            images_dir = out_dir + '/images'
            runs_dir = out_dir + '/runs'
            self.create_dir(images_dir)
            self.create_dir(runs_dir)

            row_index = 0
            for i in range(num_runs):
                if curr_data is None:
                    self.randomize_data()  # randomize the data every time
                else:
                    self.data = curr_data  # reuse the same data
                self.randomize_training_params()

                prev_step = 0
                for step in [100, 500, 1000, 2000, 4000]:
                    test_loss, train_loss = self.classifier.train(self.data, restart=False, num_steps=step - prev_step)
                    image_filename = images_dir + '/' + str(row_index) + ".png"
                    f_runs.write('\t'.join([str(row_index), image_filename]) + '\t' +
                                 self.param_str() + '\t' +
                                 '\t'.join([str(step), str(train_loss), str(test_loss)]) +
                                 '\n')
                    row_index += 1
                    self.save_plot(image_filename)
                    prev_step = step
                print(self.param_str())


if __name__ == '__main__':
    run = Run()
    run.execute_runs(run.MODE_FULL, 10)


"""
TODO:
measure time
output runs/
x1, x2, ...


VisRseq TODO:
imagepath relative to data
index.txt -> runs.txt


"""