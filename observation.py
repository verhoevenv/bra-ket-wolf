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

class RoleObservation:
  """When a character dies for any reason, their exact role is fixed,
  and game states where they do not have that role are eliminated."""
  def __init__(self,player,role):
    self.player = player
    self.role = role
  def isSupportedBy(self,universe):
    return universe.getPlayerRole(self.player) == self.role

class SeerAlignmentObservation:
  """Each time a player receives a seer vision, every game state
  in which they are the seer and their target's role does not
  match their vision is eliminated."""
  def __init__(self,player,target,vision):
    self.player = player
    self.target = target
    self.vision = vision
  def isSupportedBy(self,universe):
    if not universe.getPlayerRole(self.player) == roles.Seer():
      return True
    else:
      return universe.getPlayerRole(self.target).alignment == self.vision

class WolfAttackObservation:
  """If a character attacks another character, any game state in
  which the attacker is the dominant wolf and the target is also a
  wolf is eliminated, as wolves cannot attack other wolves."""
  def __init__(self,player,target):
    self.player = player
    self.target = target
  def isSupportedBy(self,universe):
    if not universe.getDominantWolf() == self.player:
      return True
    if universe.getPlayerRole(self.target).__class__ == roles.Wolf:
      return False
    return True

class TimeOfDeathObservation:
  """When a character is voted off, any game state in which they
  would have been killed earlier is eliminated. In particular this
  means that as soon as someone that player X has attacked is voted
  off, player X can no longer have been the dominant werewolf on
  the night they made the attack."""
  def __init__(self,player,time):
    self.player = player
    self.time = time
  def isSupportedBy(self,universe):
    if self.time[0] == "N":
      return True
    for (time,event,args) in universe.history:
      if event == "wolfkill" and time[1] < self.time[1] and args[1] == self.player:
        return False
    return True
