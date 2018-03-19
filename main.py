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

try:
   import cPickle as pickle
except:
   import pickle
from cmd import Cmd

from multiverse import Multiverse

class Main(Cmd):
  def __init__(self):
    Cmd.__init__(self)
    self.players = []
    self.roles = []
    self.keep = 1.0
    self.game = None
  def update_roles(self):
    seer = 1
    wolf = len(self.players) / 3
    villager = len(self.players) - wolf - seer
    self.roles = [("Seer",seer),("Wolf",wolf),("Villager",villager)]
  def do_start(self,s):
    """Start a new game! Requires the players and roles to be set."""
    if self.players == []:
        print "Unable to do start because players is empty"
        return
    if self.roles == []:
        print "Unable to do start because roles is empty"
        return
    self.game = Multiverse(self.players,self.roles,self.keep)
  def do_players(self,s):
    """Enter a comma-separated list of players. This will also reset
    the roles list to a sensible default."""
    if s == "":
      print self.players
    else:
      players = s.split(",")
      self.players = players
      self.update_roles()
  def do_roles(self,s):
    """Enter the roles to be used, in a format like
    roles Villager 3, Wolf 2, Seer 1"""
    if s == "":
      print self.roles
    else:
      roles = [role.strip().split(" ") for role in s.split(",")]
      roles = [(role,int(count)) for [role,count] in roles]
      self.roles = roles
  def do_keepfraction(self,s):
    """Specify which fraction of the generated universes to keep. Defaults to 1.0."""
    if s == "":
      print self.keep
    else:
      self.keep = float(s)
  def do_state(self,s):
    """Returns the current state of the game."""
    print self.game
  def do_table(self,s):
    """Returns an overview table of the distribution of good and evil."""
    print self.game.getGoodEvilDeadTable(False)
  def do_namedtable(self,s):
    """Returns an overview table of the distribution of good and evil, with player names."""
    print self.game.getGoodEvilDeadTable(True)
  def do_next(self,s):
    """Starts the next phase of the game."""
    self.game.nextPhase()
    print "It is now %s%s" % self.game.time
  def do_kill(self,s):
    """kill <player>: kills a player, fixing their role."""
    if self.game is None:
        print "Unable to do kill because game is None"
        return
    if s in self.players:
      self.game.killPlayer(s)
    else:
      print "Player {0:s} not found, did you mean 'attack {0:s}'?".format(s)
  def do_attack(self,s):
    """attack <player> <target>: wolf attack during night."""
    if self.game is None:
        print "Unable to do attack because game is None"
        return
    (player,target) = s.split(" ")
    if player in self.players and target in self.players:
      self.game.wolfAttack(player,target)
    else:
      print "Error: player {0:s} or {1:s} not found!".format(player,target)
  def do_see(self,s):
    """see <player> <target>: seer target during night.
    Note: these are executed immediately, so according to the rules
    you should input all the wolf attacks first."""
    if self.game is None:
        print "Unable to do see because game is None"
        return
    (player,target) = s.split(" ")
    if player in self.players and target in self.players:
      result = self.game.seerAlignmentVision(player,target)
      print result
    else:
      print "Error: player {0:s} or {1:s} not found!".format(player,target)
  def do_save(self,s):
    """Saves the game, by default to 'current.bra-ket-wolf' but you
    can give another file name as parameter."""
    filename = s
    if filename == "":
      filename = "current.bra-ket-wolf"
    f = open(filename,"w")
    pickle.dump(self.game,f)
    f.close()
  def do_load(self,s):
    """Loads the game, by default from 'current.bra-ket-wolf' but you
    can give another file name as parameter.
    This uses pickle so standard security warning apply, do not open untrusted files."""
    filename = s
    if filename == "":
      filename = "current.bra-ket-wolf"
    f = open(filename,"r")
    self.game = pickle.load(f)
    self.players = self.game.players
    self.roles = self.game.rolelist
    f.close()
  def do_exit(self,s):
    """Exits the program."""
    return True

if __name__ == "__main__":
  m = Main()
  m.cmdloop()
