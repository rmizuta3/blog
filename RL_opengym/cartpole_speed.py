import gym
from gym import spaces
from gym import wrappers
import numpy as np
import logging
import matplotlib.pyplot as plt
import pandas as pd


class QAgent(object):
    # エージェントの初期化
    def __init__(self, env):
        self.action_shape = env.action_space.n  # 行動の数

        # Qテーブルの生成(10*10*10*10*2)
        self.Q = np.zeros((NUM_BINS+1, NUM_BINS+1, NUM_BINS +
                           1, NUM_BINS+1, self.action_shape))
        # εの初期値
        self.epsilon = 1.0

    def bins(self, clip_min, clip_max, num):
        return np.linspace(clip_min, clip_max, num + 1)[1:-1]

    # 状態を連続値から離散値に変換
    def discretize(self, state):
        cart_pos, cart_v, pole_angle, pole_v = state
        digitized_state = [np.digitize(cart_pos, bins=self.bins(-2.4, 2.4, NUM_BINS)),  # radian 0.5 : 29
                           np.digitize(
                               cart_v, bins=self.bins(-3.0, 3.0, NUM_BINS)),
                           np.digitize(
                               pole_angle, bins=self.bins(-0.5, 0.5, NUM_BINS)),
                           np.digitize(pole_v, bins=self.bins(-2.0, 2.0, NUM_BINS))]
        return digitized_state

    def get_action(self, obs):
        # 状態を連続値から離散値に変換
        state = self.discretize(obs)

        # εの減衰
        if self.epsilon > EPSILON_MIN:
            self.epsilon -= EPSILON_DECAY

        # 活用
        if np.random.random() > self.epsilon:
            return np.argmax(self.Q[state[0], state[1], state[2], state[3]])
        # 探索
        else:
            return np.random.choice([a for a in range(self.action_shape)])

    # 収集した経験に応じてQ関数を更新
    def update_qfunc(self, state, action, reward, next_state):
        # 状態を連続値から離散値に変換
        state = self.discretize(state)
        next_state = self.discretize(next_state)

        # Q関数の更新
        Max_Q_next = np.max(
            self.Q[next_state[0], next_state[1], next_state[2], next_state[3], :])  # 選ばれた動作のQ値
        self.Q[state[0], state[1], state[2], state[3], action] = self.Q[state[0], state[1], state[2], state[3], action] + ALPHA * \
            (reward + GAMMA * Max_Q_next -
             self.Q[state[0], state[1], state[2], state[3], action])


def run(agent, env):
    ep = []
    max_speed = []
    best_step = 0
    for episode in range(NUM_EPISODES):
        state = env.reset()
        beset_speed_perstep = 0
        for step in range(MAX_STEPS):
            # 行動の取得
            action = agent.get_action(state)

            # 1ステップの実行
            next_state, reward, done, info = env.step(action)

            """倒立させたい場合
            if done:  # ステップ数が200経過するか、一定角度以上傾くとdoneはtrueになる
                if step < 195:
                    reward = -1  # 途中でこけたら罰則として報酬-1を与える
                    # self.complete_episodes = 0
                else:
                    reward = 1  # 立ったまま終了時は報酬1を与える
                    # self.complete_episodes = self.complete_episodes + 1  # 連続記録を更新
            else:
                reward = 0
            """

            # 報酬の設定
            if abs(state[0]) > 2.4:  # カートが範囲外
                reward = -1000
            else:
                reward = state[3]  # 角速度をそのまま報酬に

            # 学習
            agent.update_qfunc(state, action, reward, next_state)
            state = next_state

            # ベストstepの更新
            if beset_speed_perstep < state[3]:
                beset_speed_perstep = state[3]
            # エピソード完了
            if done:
                break

        # 動画保存用の処理(done=Trueにならないときこれがないとエラー)
        else:
            env.stats_recorder.save_complete()
            env.stats_recorder.done = True

        if best_step < beset_speed_perstep:
            best_step = beset_speed_perstep

        print(
            f"episode:{episode} best_step:{best_step} best_speed:{beset_speed_perstep} eps:{agent.epsilon} qfunc:{agent.Q.sum()}")
        ep.append(episode)
        max_speed.append(beset_speed_perstep)

        # 学習曲線の図示、保存
        if episode % 1000 == 0 and episode != 0:
            sp = pd.Series(max_speed)
            sp = sp.rolling(100).mean()
            plt.plot(ep, sp, label="max_speed")
            plt.savefig(f"graph/learningcurve_ep{episode}.png")


if __name__ == "__main__":
    # 定数(訓練)
    NUM_EPISODES = 50001  # 学習するエピソード数
    MAX_STEPS = 1000  # 1エピソードの最大ステップ数

    # 定数(学習アルゴリズム)
    EPSILON_MIN = 0.05  # 0.05  # εの最小値
    # EPSILON_DECAY = 0.0001*0.005  # ε値の減衰量
    EPSILON_DECAY = 500 * EPSILON_MIN/(NUM_EPISODES*MAX_STEPS)  # ε値の減衰量
    ALPHA = 0.5  # 学習係数（1回の学習の更新の大きさ）
    GAMMA = 0.98  # 時間割引率（0〜1）
    NUM_BINS = 10  # 離散化時の分割数

    env = gym.make('CartPole-v0')

    # 終了条件の閾値変更
    env.env.theta_threshold_radians = float('inf')
    env._max_episode_steps = MAX_STEPS  # default:200

    # 動画保存用の設定
    env = wrappers.Monitor(env, directory='movie', force=True, video_callable=(
        lambda ep: ep % 1000 == 0))  # 1000epsodeごとに動画を保存

    agent = QAgent(env)

    # 学習
    run(agent, env)
