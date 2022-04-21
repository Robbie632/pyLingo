from random import choices
import json


class Interface:

  """
  Parent class to be inherited by class for interaction with user
  """

  def __init__(self):
    pass
  def intro(self):
    pass
  def ask(self, message):
    """ask the user a phrase"""
    pass
  def correct(self):
    """give feedback that input was correct"""
    pass
  def incorrect(self):
    """give feedback that input was incorrect"""
    pass
  def check_weights(self):
    """show user probability distribution being used to 
    control picking of next phrase to ask"""
    pass
  

class CommandLine(Interface):
  """
  class for interacting with user via command line
  """

  def __init__(self):
    Interface.__init__(self)

  def intro(self):
    print("Hotkeys: s: skip, p: peek, c: check probabilities")

  def ask(self, message):
    answer = input(message)
    return answer

  def correct(self):
    print("correct")

  def incorrect(self):
    print("not quite... try again")

  def check_weights(self, weights):
    print(f"weights are \n {weights}")


class Game:

  """
  Runs the app
  """
  def __init__(self, reward, interface, syntax):
    self.weights = len(syntax) * [1]
    self.reward =reward
    self.interface=interface
    self.syntax = syntax

  def run(self):

    """
    Runs control loop 
    """
    self.interface.intro()
    next_word = True
    while True:
      if next_word:
        selected_syntax=choices(self.syntax, weights=self.weights)
        selected_index = self.syntax.index(selected_syntax[0])
        language1 = selected_syntax[0][0]
        language2 = selected_syntax[0][1]
        
      else:
        next_word = True
      tries = 0
      while True:
        answer = self.interface.ask(language1+":"+"\n")
        answer = self.preprocess(answer) 
        if answer == "s":
          self.weights[selected_index]+=(self.reward*2)
          break
        elif answer=="p":
          print(language2)
          next_word=False
          self.weights[selected_index]+=self.reward
          break
        if answer == "c":
          self.interface.check_weights(self.weights)
          break
        processed_swedish = self.preprocess(language2)
        if answer!=processed_swedish and tries < 3:
          self.weights[selected_index]+=self.reward
          self.interface.incorrect()
          hint = self.uppercase_incorrect_words(answer, processed_swedish)
          print(hint)
          tries = tries + 1
          continue
        elif answer!=language2 and tries == 3:
          print(f"the answer is:\n {language2} ")
          tries = 0
          self.weights[selected_index]+=self.reward
          continue
        else:
          self.weights[selected_index] = max(1, self.weights[selected_index]-self.reward)
          self.interface.correct()
          break

  def preprocess(self, sentence):
    """
    preprocess a sentence
    """
    sentence = sentence.lower()
    sentence = sentence.strip()
    sentence = sentence.replace("-", " ")
    return sentence
  
  def uppercase_incorrect_words(self, attempt, truth):
    """
    returns string with incorrect words in uppercase
    """
    out = []
    for a, t in zip(attempt.split(), truth.split()):
      if a != t:
        out.append(a.upper())
      else:
        out.append(a.lower())
    out = " ".join(out)
    return out


if __name__=="__main__":
  
  with open("phrases.json", "r") as f:
    phrases = json.load(f)
    
  clt = CommandLine() 
  myGame = Game(2, clt, phrases["syntax"])
  myGame.run()
