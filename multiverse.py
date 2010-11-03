# Copyright 2010 Vincent Verhoeven
#
# This file is part of bra-ket-wolf.
#
# bra-ket-wolf is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# bra-ket-wolf is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with bra-ket-wolf.  If not, see <http://www.gnu.org/licenses/>.

from universe import Universe
import roles
import observation
from algorithms import next_permutation

from itertools import permutations, repeat, chain
from collections import defaultdict
import pprint
import random

def expandrolelist(rolelist):
  result = []
  for (role,count) in rolelist:
    for i in range(count):
      result.append(roles.getNewRole(role))
  return result

class Multiverse:
  def __init__(self,players,rolelist,keepFraction=1.0):
    self.players = list(players)
    random.shuffle(self.players)
    self.rolelist = rolelist
    self.toKeep = keepFraction
    self.universes = self.generateUniverses()
    self.observations = []
    self.time = ("N",0)

  def __str__(self):
    time = "Stats at %s%s" % self.time
    roles = pprint.pformat(self.gatherAllRoleProbabilities())
    dead = pprint.pformat(self.gatherDeadProbabilities())
    univ = len(self.universes)
    return "%s\n%s\n%s\n%s\n" % (time,roles, dead, univ)

  def getGoodEvilDeadTable(self,names=True):
    if names:
      headers = "Player Name Good Evil Dead".split(" ")
    else:
      headers = "Player Good Evil Dead".split(" ")
    rows = [headers]
    roleprobs = self.gatherAllRoleProbabilities()
    dead = self.gatherDeadProbabilities()
    for (i,player) in enumerate(self.players):
      probs = roleprobs[player]
      good = sum([v for (k,v) in probs.items() if k.alignment == roles.VillageAlignment])
      evil = sum([v for (k,v) in probs.items() if k.alignment == roles.WolfAlignment])
      dead = self.getDeadness(player)
      if names:
        rows.append([str(i+1),player,"{0:.2%}".format(good),"{0:.2%}".format(evil),"{0:.2%}".format(dead)])
      else:
        rows.append([str(i+1),"{0:.2%}".format(good),"{0:.2%}".format(evil),"{0:.2%}".format(dead)])
    lens = [0] * len(headers)
    for row in rows:
      for (i,cell) in enumerate(row):
        if len(cell) > lens[i]:
          lens[i] = len(cell)
    s = "  ".join(['{' + str(i) +':<' + str(l) + '}' for (i,l) in enumerate(lens)])
    rowsformatted = [s.format(*row) for row in rows]
    return "\n".join(rowsformatted)

  def nextPhase(self):
    if self.isNight():
      self.time = ("D",self.time[1] + 1)
    else:
      self.time = ("N",self.time[1])

  def isNight(self):
    return self.time[0] == "N"

  def generateUniverses(self):
    result = []
    for assignment in next_permutation(sorted(expandrolelist(self.rolelist))):
      assignedroles = dict(zip(self.players,assignment))
      result.append(Universe(assignedroles,self))
    numUniverses = int(self.toKeep * len(result))
    filteredUniverses = random.sample(result,numUniverses)
    return filteredUniverses

  def gatherAllRoleProbabilities(self):
    result = {}
    for p in self.players:
      result[p] = self.gatherRoleProbabilities(p)
    return result

  def gatherRoleProbabilities(self,player):
    roles = defaultdict(int)
    for u in self.universes:
      roles[u.getPlayerRole(player)] += 1
    return dict([(k,float(v)/len(self.universes)) for (k,v) in roles.items()])

  def gatherDeadProbabilities(self):
    return dict([(p,self.getDeadness(p)) for p in self.players])

  def addObservation(self,observation):
    keptuniverses = []
    for u in self.universes:
      if observation.isSupportedBy(u):
        keptuniverses.append(u)
    self.universes = keptuniverses
    self.observations.append(observation)

  def wolfAttack(self,player,target):
    assert(self.isNight())
    for u in self.universes:
      u.wolfAttack(player,target)
    self.addObservation(observation.WolfAttackObservation(player,target))

  def seerAlignmentVision(self,player,target):
    assert(self.isNight())
    assert(not self.isDead(player))
    assert(roles.Seer() in self.gatherRoleProbabilities(player))
    vision = self.randomUniverse().assignment[target].alignment
    self.addObservation(observation.SeerAlignmentObservation(player,target,vision))
    return vision

  def getDeadness(self,player):
    c = len([u for u in self.universes if u.isDead(player)])
    return float(c)/len(self.universes)

  def isDead(self,player):
    return self.getDeadness(player) == 1

  def killPlayer(self,player):
    for u in self.universes:
      u.killPlayer(player)
    self.addObservation(observation.TimeOfDeathObservation(player,self.time))
    self.propagateDeaths()

  def canHaveRole(self,player,role):
    roles = self.gatherRoleProbabilities(player).keys()
    return any([r.__class__.__name__ == role for r in roles])

  def propagateDeaths(self):
    change = True
    while change:
      change = False
      for p in self.players:
        if self.isDead(p) and len(self.gatherRoleProbabilities(p)) > 1:
          change = True
          fixedrole = self.randomUniverse().getPlayerRole(p)
          self.addObservation(observation.RoleObservation(p,fixedrole))

  def randomUniverse(self):
    return random.choice(self.universes)
