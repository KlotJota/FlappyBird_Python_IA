# FlappyBird_Python_IA
<p>Neste projeto, desenvolvi o jogo FlappyBird utilizando Python. O objetivo final é desenvolver uma IA que aprende a jogar e o faz sozinha.</p>
 
<p>Neste projeto foi utilizada a rede neural NEAT (NeuroEvolution of Augmenting Topologies). A princípio, foi criado uma cópia do jogo "FlappyBird", totalmente jogável e funcional.</p> 
 
<img src="https://github.com/KlotJota/FlappyBird_Python_IA/blob/main/FlappyBird_GIF.gif" width="200" height="270"/>
 
<p>O objetivo final foi fazer com que a IA aprendesse a jogar o jogo e se tornasse imortal.</p>
<p>De modo resumido, a rede neural funciona da seguinte forma: ela trabalha com gerações de pássaro, sendo que cada geração contém 100 pássaros. Ela recebe algumas informações, tais como altura do pássaro, ditância do próximo cano de cima e de baixo. Com essas informações e alguns cálculos aleatoriamente gerados pela rede neural, ela toma uma decisão: <b>pular ou não.</b></p>
<p>Conforme uma geração de pássaros é inteiramente eliminada, ela mantém os 2 último melhores pássaros e faz modificações minúsculas nos cálculos, e cria uma nova geração inteira com base nesses pássaros. Ela repete esse processo até que exista um pássaro tão bom que se torna imortal no jogo.</p>
 
<img src="https://github.com/KlotJota/FlappyBird_Python_IA/blob/main/FlappyBirdIA_GIF.gif" width="200" height="270"/>

<p>Código realizado com base em aulas do canal Hashtag Programação no Youtube</p>
