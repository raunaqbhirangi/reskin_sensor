import pygame
import sys
from pygame.locals import *
import math
import time
import numpy as np
from reskin_sensor import ReSkinBase

def init_pygame():
    time.sleep(1)
    pygame.init() # initialize pygame
    clock = pygame.time.Clock()
    screen = pygame.display.set_mode((420,600))
    bg = pygame.image.load("./images/3D.PNG")
    pygame.mouse.set_visible(1)

    pygame.display.set_caption('5X Board Visual')
    return clock, screen, bg

def get_baseline(sens, num_samples):
    print("Leave board resting on table")
    time.sleep(2.)

    baseline_samples = sens.get_data(num_samples)
    baseline = [s.data for s in baseline_samples]
    baseline = np.array(baseline)
    baseline = np.mean(baseline, axis=0)
    print("Resting data collected.")

    return baseline


if __name__ == '__main__':
    
    WHITE = pygame.Color(255, 255, 255)
    RED = pygame.Color(255, 0, 0) 
    BLACK = pygame.Color(0,0,0)

    viz_sensor = ReSkinBase(num_mags=5, port='/dev/ttyACM0', baudrate=115200)
    scale = 100

    temp_mask = np.ones((20,),dtype=bool)
    temp_mask[::4] = False
    
    clock, screen, bg = init_pygame()
    
    # read first 100 samples as baseline
    numBaselineSamples = 100

    baseline = get_baseline(viz_sensor, numBaselineSamples)

    # chip locations in pixels on the game board
    # in order of center, top, right, bottom, left to match incoming data stream
    chip_locations = np.array([[211,204], [211, 60],[357, 206],[211, 353],[67, 204]])

    while True:

        raw_data = viz_sensor.get_data(1)
        input_data = raw_data[0].data - baseline
        #rotation of chip axes to pygame coordinate system

        input_data = input_data[temp_mask]
        input_data[0:3] = [input_data[1], -1*input_data[0], -1*input_data[2]]
        input_data[3:6] = [input_data[4], -1*input_data[3], -1*input_data[5]]
        input_data[6:9] = [input_data[6], input_data[7], -1*input_data[8]]
        input_data[9:12] = [-1*input_data[9], -1*input_data[10], -1*input_data[11]]
        input_data[12:15] = [-1*input_data[13], input_data[12], -1*input_data[14]]

        screen.blit(bg, (0,0))
        for idx in range(5):
            center_arrow = chip_locations[idx]
            angle = math.atan2(input_data[3*idx+1],input_data[3*idx])
            z = math.sqrt((input_data[3*idx]*input_data[3*idx]+input_data[3*idx+1]*input_data[3*idx+1]))
            x = center_arrow[0] + math.sin(angle)*z
            y = center_arrow[1] + math.cos(angle)*z
            r = abs(input_data[3*idx+2])/scale
            pygame.draw.line(screen, (0,0,0), center_arrow, (x,y), 5)
            pygame.draw.circle(screen, (0,0,1), center_arrow, r, 1)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == KEYDOWN:
                if event.key == ord('b'):
                    baseline = get_baseline(viz_sensor, numBaselineSamples)

        pygame.display.update()