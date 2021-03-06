import os.path
import ast
from agent import Agent
from keras.models import load_model
from environment import Environment

WIDTH = 84
HEIGHT = 84
N_FRAMES = 3

class Player:
	def __init__(self):
		self.space_invader = Environment('SpaceInvaders-v0')
		self.agent = Agent(HEIGHT, WIDTH, self.space_invader.env.action_space.n)
		self.weights_filename = "weights.h5"
		self.config_filename = 'config.txt'
		self.score_filename = 'score.txt'

	def train(self):
		itr, avg, max_score = self.load_config()
		try:
			while itr < 300000:
				reward, q_val, count = self.space_invader.train(self.agent)

				if reward > max_score:
					max_score = reward

				if itr % 20 == 0:
					self.agent.decay()

				if itr % 1000 == 0 and itr != 0:
					if itr % 3500 == 0:
						self.perform_quicksave(itr, avg, max_score, save_memory=True)
					else:
						self.perform_quicksave(itr, avg, max_score)

				string = str(reward) + " " + str(q_val) + " Itr: " + str(itr) + " " + str(count) + " Max " + str(max_score) + "\n"
				self.quick_write(string)

				if reward >= avg and itr > 500:
					avg = self.perform_earlystop(avg)
				itr += 1
		finally:
			self.perform_quicksave(itr, avg, max_score, save_memory=True)


	def perform_earlystop(self, avg):
		itr = 0
		total_reward = 0
		while itr < 15:
			reward, q_val = self.space_invader.test(self.agent)
			total_reward += reward
			itr += 1

		if avg <= total_reward/15.0:
			if os.path.isfile("best_performace_" + str(avg) + ".h5"):
				os.remove("best_performace_" + str(avg) + ".h5")
			avg = total_reward/15.0
			self.agent.model.save("best_performace_" + str(avg) + ".h5")
		return avg


	def test(self):
		self.load_config(test=True)
		itr = 0
		try:
			while itr < 100:
				reward, q_val = self.space_invader.test(self.agent)
				string = "Reward: " + str(reward) + " Q value: " + str(q_val) + " Iteration: " + str(itr)
				print string
				itr += 1

		finally:
			pass

	def perform_quicksave(self, itr, avg, max_score, save_memory=False):
		self.agent.model.save(self.weights_filename)

		config_file = open(self.config_filename, 'w')
		config = {"itr":itr, "eps":self.agent.eps, "avg":avg, "max_score":max_score}

		config_file.write(str(config))
		config_file.close()

		if save_memory:
			self.agent.memory.save_memory()


	def load_config(self, test=False):
		if os.path.isfile(self.weights_filename):
			self.agent.model = load_model(self.weights_filename)
			self.agent.memory.load_memory()
			print "Weights loaded"

		if os.path.isfile(self.config_filename):
			config_file = open(self.config_filename, 'r')

			config = ast.literal_eval(config_file.read())
			itr = int(config["itr"])
			avg = float(config["avg"])
			max_score = float(config["max_score"])
			if test and avg != -1:
				self.agent.model = load_model("best_performace_" + str(avg) + ".h5")
			self.agent.eps = float(config["eps"])
			config_file.close()
			print "Config loaded"
			return itr, avg, max_score

		return 0, -1.0, -1.0


	def quick_write(self, string):
		target = open(self.score_filename, 'a')
		target.write(string)
		target.close()

player1 = Player()
player1.train()
