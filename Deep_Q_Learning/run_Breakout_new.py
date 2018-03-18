import gym
from CNN_Brain import CNN_Brain as brain
from Agent import Agent
import numpy as np
from video_env import video_env
# import blosc
import scipy.ndimage as ndimage

env = gym.make('Breakout-v0')   # 定义使用 gym 库中的那一个环境


print(env.action_space.n)  # 查看这个环境中可用的 action 有多少个
print(env.observation_space)    # 查看这个环境中可用的 state 的 observation 有多少个
# print(env.observation_space.high)   # 查看 observation 最高取值
# print(env.observation_space.low)    # 查看 observation 最低取值


Brain = brain(n_actions=env.action_space.n,
              observation_width=84,
              observation_height=84,
              observation_depth=4,
              filters_per_layer=np.array([32, 64, 64]),
              restore=False,
              output_graph=False)
RL = Agent(
    brain=Brain,
    n_actions=env.action_space.n,
    observation_space_shape=env.observation_space.shape,
    reward_decay=0.99,
    MAX_EPSILON=1,  # epsilon 的最大值
    MIN_EPSILON=0.1,  # epsilon 的最小值
    replace_target_iter=10000,
    memory_size=1000000,
    batch_size=32,
)


def concatenate(screens):
    return np.concatenate(screens, axis=2)


def preprocess(screen):
    screen = np.dot(screen, np.array([.299, .587, .114])).astype(np.uint8)
    screen = ndimage.zoom(screen, (0.4, 0.525))
    screen.resize((84, 84, 1))
    return screen


env = video_env(env)
total_steps = 0

for i_episode in range(100000):

    observation = env.reset()
    observation = preprocess(observation)
    # print(type(observation), observation)
    ep_r = 0
    totalR = 0
    observation_input = [observation, observation, observation, observation]
    state = concatenate(observation_input)
    while True:
        # env.render()

        action = RL.choose_action(state)

        observation_, reward, done, info = env.step(action)

        totalR += reward

        if (len(observation_input) == 4):

            observation_ = preprocess(observation_)
            observation_input.insert(0, observation_)
            observation_input.pop(4)
            state_ = concatenate(observation_input)
            # print(state.shape)
            # clipped all positive rewards at 1 and all negative rewards at -1, leaving 0 rewards unchanged.
            clippedReward = min(1, max(-1, reward))
            RL.store_memory(state, action, clippedReward, state_, done)

        if len(RL.memory) > 50000:
            RL.learn()
        if done:
            print('episode: ', i_episode,
                  ' epsilon: ', round(RL.epsilon, 2),
                  'total_reward:', totalR)
            break

        state = state_

        total_steps += 1

Brain.save()