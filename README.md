<h1 align="center">
  Auto Maple
</h1>

Auto Maple is a Python program that plays MapleStory, a 2D side-scrolling MMORPG, using 
simulated key presses, TensorFlow machine learning, template matching, and other computer 
vision techniques.



<h2 align="center">
  The Minimap
</h2>
<img align="right" src="https://user-images.githubusercontent.com/69165598/123177212-b16f0700-d439-11eb-8a21-8b414273f1e1.gif" width="400"/>

Auto Maple uses OpenCV template matching to determine the bounds of the minimap as well as the various elements within it, allowing it to accurately track
the player's in-game position. If "record_layout" is set to "True" in the routine file, then Auto Maple will record the player's previous positions in a quadtree-based Layout object, which is periodically saved to a file in the "layouts" directory. This Layout object uses the A* search algorithm on its stored points to calculate the shortest path from the player to any target location, which can dramatically improve the accuracy and speed at which routines are executed.

<br clear="right"/>



<h2 align="center">
  Command Books
</h2>

Designed with modularity in mind, Auto Maple can operate any character
in the game as long as it is provided with an appropriate list of in-game actions, or a
"command book". A command book is a Python file that contains multiple classes, one for 
each in-game ability, that tells the bot what keys it should press and when to press them.

<h2 align="center">
  Runes
</h2>

<h2 align="center">
  Routines
</h2>

<h2 align="center">
  Video Demonstration
</h2>

<p align="center">
  <a href="https://www.youtube.com/watch?v=qs8Nw55edhg">
    <img src="https://img.youtube.com/vi/qs8Nw55edhg/0.jpg"/>
  </a>
</p>
