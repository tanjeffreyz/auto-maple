<h1 align="center">
  Auto Maple
</h1>

Auto Maple is a Python program that plays MapleStory, a 2D side-scrolling MMORPG, using simulated key presses, TensorFlow machine learning, OpenCV template matching, and other computer vision techniques.

<br>








<h2 align="center">
  Minimap
</h2>

<table align="center" border="0">
  <tr>
    <td>
Auto Maple uses OpenCV template matching to determine the bounds of the minimap as well as the various elements within it, allowing it to accurately track the player's in-game position. If "record_layout" is set to "True" in the routine file, Auto Maple will record the player's previous positions in a quadtree-based Layout object, which is periodically saved to a file in the "layouts" directory. Every time a new routine is loaded, its corresponding layout file, if it exists, will also be loaded. This Layout object uses the A* search algorithm on its stored points to calculate the shortest path from the player to any target location, which can dramatically improve the accuracy and speed at which routines are executed.
    </td>
    <td align="center" width="400px">
      <img align="center" src="https://user-images.githubusercontent.com/69165598/123177212-b16f0700-d439-11eb-8a21-8b414273f1e1.gif"/>
      <br>
      <sub>
      Click <a href="https://github.com/tanjeffreyz02/Auto-Maple/blob/version-2/routines/hft.csv">here</a> to view the above routine.
      </sub>
    </td>
  </tr>
</table>

<br>








<h2 align="center">
  Command Books
</h2>

<p align="center">
  <img src="https://user-images.githubusercontent.com/69165598/123372905-502e5d00-d539-11eb-81c2-46b8bbf929cc.gif" width="900px"/>
</p>
  
<table align="center" border="0">
  <tr>
    <td width="900px">
Designed with modularity in mind, Auto Maple can operate any character in the game as long as it is provided with a list of in-game actions, or a "command book". A command book is a Python file that contains multiple classes, one for each in-game ability, that tells the program what keys it should press and when to press them. Once a command book is imported, its classes are automatically compiled into a dictionary that Auto Maple can then use to interpret commands within routines. Commands have access to all of Auto Maple's global variables, which can allow them to actively change their behavior based on the player's position and the state of the game.
<br><br>
The above video shows Auto Maple consistently performing a mechanically advanced ability combination.
    </td>
  </tr>
</table>
  
<br>







<h2 align="center">
  Routines
</h2>

<table align="center" border="0">
  <tr>
    <td width="300px">
      <p align="center">
        <a href="https://user-images.githubusercontent.com/69165598/129115704-d702944d-fc6e-4bfb-919f-0d9328be8cd2.jpg">
          <img src="https://user-images.githubusercontent.com/69165598/129115666-7e366738-0249-47ea-8cc1-6ce8a57593a5.jpg"/>
        </a>
        <br>
        <sub>
          Click <a href="https://github.com/tanjeffreyz02/Auto-Maple/blob/version-2/routines/mts3.csv">here</a> to view the entire routine.
        </sub>
      </p>
    </td>
    <td>
      <p>
A routine is a user-created CSV file that tells Auto Maple where to move and what abilities and commands to use at each location. A custom-made interpreter within Auto Maple parses through the selected routine and converts it into a list of objects that can then be executed by the program. An error message is printed for every line that contains invalid parameters, and those lines are ignored during the conversion.
    
**Points** are created using `*, <x position>, <y position>` <br>
Each point stores the commands below it and will execute them in that order once the character reaches that point. There are also a couple optional keyword arguments:
        <br>
<sub>- **"adjust"**: Fine-tunes character position to be within `adjust_tolerance` (a routine setting). </sub>
        <br>
<sub>- **"frequency"**: How often to execute this point. </sub>
        <br>
<sub>- **"counter"**: Set's the initial value of this point's counter. A point's counter increments every cycle (wrapped back to 0 at `frequency`), and the point will only execute if its counter is 0. </sub>

**Labels** are created using `@, <label name>` <br>
They can be jumped to using the "goto" command, which allows users to create loops and organize routines into sections.

**Commands** are created using `<command name>, <p1>, <p2>, ...` <br>
`<command name>` corresponds with the class names inside command book files, and `<p1>, <p2>, ...` correspond with the class's `__init__` parameters. Keyword arguments are also supported.
        
**Settings** are updated using `s, <setting name>, <value>` <br>
All the editable settings can be found at the bottom of [config.py](https://github.com/tanjeffreyz02/Auto-Maple/blob/version-2/config.py).
    </p>
    </td>
  </tr>
</table>

<br>








<h2 align="center">
  Runes
</h2>

<p align="center">
  <img src="https://user-images.githubusercontent.com/69165598/123479558-f61fad00-d5b5-11eb-914c-8f002a96dd62.gif" width="900px"/>
</p>

<table align="center" border="0">
  <tr>
    <td width="900px">
Auto Maple has the ability to automatically solve "runes", or in-game arrow key puzzles. It first uses OpenCV's color filtration and Canny edge detection algorithms to isolate the arrow keys and reduce as much background noise as possible. Then, it runs multiple inferences on the preprocessed frames using a custom-trained 
    <a href="https://drive.google.com/drive/folders/1SPdTNF4KZczoWyWTgfyTBRvLvy7WSGpu?usp=sharing">TensorFlow model</a>
until two inferences agree. Because of this preprocessing, Auto Maple is extremely accurate at solving runes in all kinds of (often colorful and chaotic) environments.
    </td>
  </tr>
</table>


<br>









<h2 align="center">
  Video Demonstration
</h2>

<p align="center">
  Click below to see Auto Maple in action:
</p>

<p align="center">
  <a href="https://www.youtube.com/watch?v=qs8Nw55edhg">
    <img src="https://user-images.githubusercontent.com/69165598/123308656-c5b61100-d4d8-11eb-99ac-c465665474b5.gif" width="600px"/>
  </a>
</p>

<br>








<h2 align="center">
  Reflection
</h2>

From working on this project, I truly learned a lot. Auto Maple not only allowed me to apply the knowledge I gained in class to a challenging problem, but it also introduced me to many exciting and complex concepts such as machine learning and Canny edge detection. However, perhaps more importantly, working on Auto Maple has given me a deeper appreciation of human problem solving and a clearer understanding of just how hard it is for a computer to emulate that.

Early in this project, when I was still trying to get the character to move to locations on the minimap, I resorted to letting the program blindly move horizontally and vertically until it reached its target. This was very inefficient and often resulted in the character getting stuck. Later, I realized that memory was the main aspect Auto Maple was missing: human gamers remember where they've been, which places are safe to walk on, and which places aren't. This gave me the idea to create a Layout class to help the program chart a path in advance based on where it has already been, much like a human.

In the end, Auto Maple is still far from perfect. It can't predict and prevent missteps like we can. It can't reproduce the fluid actions of a practiced gamer. But acknowledging these shortcomings inspires me to continue learning and experimenting with new ways to make programs faster and smarter.
