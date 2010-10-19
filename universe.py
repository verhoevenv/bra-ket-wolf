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

import roles

class Universe:
  def __init__(self, playerassignment, multiverse):
    self.assignment = playerassignment
    self.multiverse = multiverse
    self.deadplayers = []
    self.history = []

  def getPlayerRole(self,player):
    return self.assignment[player]

  def isDead(self,player):
    return player in self.deadplayers

  def getDominantWolf(self):
    maxp = None
    minr = 100000
    for (p,r) in self.assignment.items():
      if r.__class__ == roles.Wolf and r.rank < minr:
        maxp = p
        minr = r.rank
    return maxp

  def wolfAttack(self,player,target):
    if self.assignment[player].__class__ != roles.Wolf:
      return
    if self.assignment[target].__class__ == roles.Wolf:
      return
    if target in self.deadplayers:
      return

    if self.getDominantWolf() == player:
      self.killPlayer(target)
      self.addHistory("wolfkill",(player,target))

  def killPlayer(self,player):
    self.deadplayers.append(player)
    self.addHistory("death",(player,))

  def addHistory(self,event,args):
    currtime = self.multiverse.time
    self.history.append((currtime,event,args))
