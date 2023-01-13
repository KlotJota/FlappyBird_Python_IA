import pygame   # necessário para o jogo
import os       # permite a integração com arquivos do computador
import random   # geração de numeros aleatórios para os obstáculos do jogo
import neat

ia_jogando = True   # define se a ia está jogando ou o usuário
geracao = 0         # geração de passaros

# CONSTANTES:

TELA_LARGURA = 500
TELA_ALTURA = 680

IMAGEM_OBSTACULO = pygame.transform.scale2x(pygame.image.load(os.path.join('imagens','pipe.png')))      # é necessário o uso do os ja que a pasta
IMAGEM_CHAO = pygame.transform.scale2x(pygame.image.load(os.path.join('imagens','base.png')))                                                                                           #  "imagens" nao se encontra no msm local
IMAGEM_FUNDO = pygame.transform.scale2x(pygame.image.load(os.path.join('imagens','bg.png')))                                                                                       # scale 2x para dobrarmos o tamanho das imagens

IMAGENS_PASSARO = [
    pygame.transform.scale2x(pygame.image.load(os.path.join('imagens','bird1.png'))),
    pygame.transform.scale2x(pygame.image.load(os.path.join('imagens','bird2.png'))),
    pygame.transform.scale2x(pygame.image.load(os.path.join('imagens','bird3.png')))    # lista de imagens
]

pygame.font.init()
FONTE_PONTOS = pygame.font.SysFont('calibri', 30)

class Passaro:
    IMAGENS = IMAGENS_PASSARO

    # animações de rotação do pássaro
    ROTACAO_MAX = 25
    VELOCIDADE_ROTACAO = 20
    TEMPO_ANIMACAO = 5

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.angulo = 0
        self.velocidade = 0 # movimento vertical
        self.altura = self.y
        self.tempo = 0  # tempo de animação (movimento de parábola)
        self.contagem_imagem = 0    # saber qual imagem do passaro que usará
        self.imagem = self.IMAGENS[0]

    def pular(self):
        self.velocidade = -9 # velocidade do pulo (y cresce pra baixo no pygame, por isso o valor negativo)
        self.tempo = 0
        self.altura = self.y

    def mover(self):
        # calcular o deslocamento x (pra direita)
        self.tempo += 1
        deslocamento = 1.5 * (self.tempo**2) + self.velocidade * self.tempo    # fórmula do deslocamento - S = so + vot.at²/2

        # restringir esse deslocamento (restringir algumas possibilidades)
        if deslocamento > 16:
            deslocamento = 16
        elif deslocamento < 0:
            deslocamento -= 2   # extende o tamanho do pulo

        self.y += deslocamento

        # ângulo do pássaro
        if deslocamento < 0 or self.y < (self.altura): # assim, o angulo de queda so mudara quando ele chegar a linha de partida novamente
            if self.angulo < self.ROTACAO_MAX:
                self.angulo = self.ROTACAO_MAX

        else:
            if self.angulo > -90:
                self.angulo -= self.VELOCIDADE_ROTACAO

    def desenhar(self, tela): # relacionado à posição de aparecimento do pássaro e maneira como vai aparecer na tela
        # definir a imagem do pássaro usada
        self.contagem_imagem += 1

        if self.contagem_imagem < self.TEMPO_ANIMACAO:  # animação do bater de asas, para baixo e vice-versa
            self.imagem = self.IMAGENS[0]
        elif self.contagem_imagem < self.TEMPO_ANIMACAO * 2:
            self.imagem = self.IMAGENS[1]
        elif self.contagem_imagem < self.TEMPO_ANIMACAO * 3:
            self.imagem = self.IMAGENS[2]
        elif self.contagem_imagem < self.TEMPO_ANIMACAO * 4:
            self.imagem = self.IMAGENS[1]
        elif self.contagem_imagem >= self.TEMPO_ANIMACAO * 4 + 1:
            self.imagem = self.IMAGENS[0]
            self.contagem_imagem = 0    # zera o loop de imagens e volta ao início

        # se o pássaro estiver caindo, não deve bater as asas
        if self.angulo <= -80:
            self.imagem = self.IMAGENS[1]
            self.contagem_imagem = self.TEMPO_ANIMACAO * 2  # proximo bater de asas após cair é para baixo

        # desenhar a imagem
        imagem_rotacionada = pygame.transform.rotate(self.imagem, self.angulo)
        pos_centro_imagem = self.imagem.get_rect(topleft = (self.x, self.y)).center # centro da tela
        retangulo = imagem_rotacionada.get_rect(center = pos_centro_imagem)
        tela.blit(imagem_rotacionada, retangulo.topleft)

    def get_mask(self): # em termos gerais, melhorará a colisão do pássaro, não levando em conta apenas o retangulo em volta dele
        return pygame.mask.from_surface(self.imagem)

class Cano:
    DISTANCIA = 200 # (de um cano para outro, cima e baixo)
    VELOCIDADE = 5

    def __init__(self, x):
        self.x = x
        self.altura = 0
        self.pos_topo = 0
        self.pos_base = 0
        self.CANO_TOPO = pygame.transform.flip(IMAGEM_OBSTACULO, False, True)   # flipar apenas da vertical
        self.CANO_BASE = IMAGEM_OBSTACULO
        self.passou = False # passou do cano ou não
        self.definir_altura()

    def definir_altura(self):
        self.altura = random.randrange(50, 400) # para não termos canos nem muito ao topo nem muito abaixo
        self.pos_topo = self.altura - self.CANO_TOPO.get_height()
        self.pos_base = self.altura + self.DISTANCIA

    def mover(self):
        self.x -= self.VELOCIDADE

    def desenhar(self, tela):
        tela.blit(self.CANO_TOPO, (self.x, self.pos_topo))
        tela.blit(self.CANO_BASE, (self.x, self.pos_base))

    def colidir(self, passaro):
        passaro_mask = passaro.get_mask()
        topo_mask = pygame.mask.from_surface(self.CANO_TOPO)    # mesmo processo de melhora de colisão feito no pássaro
        base_mask = pygame.mask.from_surface(self.CANO_BASE)

        distancia_topo = (self.x - passaro.x, self.pos_topo - round(passaro.y)) # precisa ser numero inteiro
        distancia_base = (self.x - passaro.x, self.pos_base - round(passaro.y)) # precisa ser numero inteiro

        topo_ponto = passaro_mask.overlap(topo_mask, distancia_topo) # ambos conferem se ha colisão dos canos com o pássaro
        base_ponto = passaro_mask.overlap(base_mask, distancia_base)

        if base_ponto or topo_ponto:    # se houve colisão retornar True, se não, False
            return True
        else:
            return False

class Chao:
    VELOCIDADE = 5  # mesma do cano
    LARGURA = IMAGEM_CHAO.get_width()
    IMAGEM = IMAGEM_CHAO

    def __init__(self, y):
        self.y = y
        self.x1 = 0
        self.x2 = self.LARGURA

    def mover(self):
        self.x1 -= self.VELOCIDADE
        self.x2 -= self.VELOCIDADE

        if self.x1 + self.LARGURA < 0:
            self.x1 = self.x2 + self.LARGURA
        if self.x2 + self.LARGURA < 0:
            self.x2 = self.x1 + self.LARGURA

    def desenhar(self, tela):
        tela.blit(self.IMAGEM, (self.x1, self.y))
        tela.blit(self.IMAGEM, (self.x2, self.y))

def desenhar_tela(tela, passaros, canos, chao, pontuacao):
    tela.blit(IMAGEM_FUNDO, (0, 0))
    for passaro in passaros:
        passaro.desenhar(tela)
    for cano in canos:
        cano.desenhar(tela)

    texto = FONTE_PONTOS.render(f"Pontuação: {pontuacao}", 1, (255, 255, 255))
    tela.blit(texto, (TELA_LARGURA - 10 - texto.get_width(), 10))

    if ia_jogando:  # só se aplicará caso a IA for o jogador
        texto = FONTE_PONTOS.render(f"Geração: {geracao}", 1, (255, 255, 255))
        tela.blit(texto, (10, 10))

    chao.desenhar(tela)

    pygame.display.update() # update na tela para a mesma ser desenhada

def main(genomas, config):         # fitness function (nos dirá quanto bem um pássaro foi). Por padrão PRECISA receber 2 parâmetros
    global geracao  # variável global, criada no início do código
    geracao += 1    # contagem de gerações

    if ia_jogando:  # caso for a IA jogando, criar diversos pássaros
        redes = []          # rede neural em si, criada, que usa as configurações definidas nos genomas
        lista_genomas = []  # são as configs da rede neural
        passaros = []
        for _, genoma in genomas:   # para cada pássaro, ele terá um genoma e uma rede neural
            rede = neat.nn.FeedForwardNetwork.create(genoma, config)  # criação de rede neural feedforward (esquerda pra direita)
            redes.append(rede)
            genoma.fitness = 0  # fitness é uma pontuação interna que diz à IA se o pássaro é bom ou não. Quanto mais longe ele chegar, mais pontuação ele terá aqui. Com isso, a rede neural procura entender quais ações lhe da mais pontos e quais tiram, procurando sempre mais pontuação.
            lista_genomas.append(genoma)
            passaros.append(Passaro(230, 350))

    else:           # caso for o usuario, criar apenas um passaro
        passaros = [Passaro(230, 350)]
    chao = Chao(630)
    canos = [Cano(700)]
    tela = pygame.display.set_mode((TELA_LARGURA, TELA_ALTURA))
    pontuacao = 0
    relogio = pygame.time.Clock()

    rodando = True

    while rodando:
        relogio.tick(30)    # frames por segundo (fps)

        # interação com o jogador
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:  # caso o jogador clicar no X para fechar o jogo
                rodando = False
                pygame.quit()
                quit()  # fecha o jogo
            if not ia_jogando:  # a barra de espaço só funcionará caso o usuário for o jogador
                if evento.type == pygame.KEYDOWN:
                    if evento.key == pygame.K_SPACE:
                        for passaro in passaros:
                            passaro.pular()

        indice_cano = 0
        if len(passaros) > 0:
            if len(canos) > 1 and passaros[0].x > canos[0].x + canos[0].CANO_TOPO.get_width():  # caso a posiçao x do primeiro passaro for maior que a posicao x + largura do cano, significa que o passaro ja passou de um cano e deverá olhar a posição do proximo
                indice_cano = 1
        else:
            rodando = False
            break

        # movimentação dos objetos
        for i, passaro in enumerate(passaros):
            passaro.mover()

            # aumentar um pouco a fitnesse do pássaro
            if ia_jogando:
                lista_genomas[i].fitness += 0.1 # a distancia do passaro aumentara apenas um pouco da pontuaçao do fitness
                output = redes[i].activate((passaro.y,
                                            abs(passaro.y - canos[indice_cano].altura),
                                            abs(passaro.y - canos[indice_cano].pos_base)))  # 3 inputs, como definido anteriormente (pos y, distancia do cano de baixo e de cima)
                # output fica entre -1 e 1 -> se o output for > 0.5, o pássaro irá pular
                if output[0] > 0.5:
                    passaro.pular()

        chao.mover()

        adicionar_cano = False
        remover_canos = []

        for cano in canos:
            for i, passaro in enumerate(passaros):
                if cano.colidir(passaro):
                    passaros.pop(i)
                    if ia_jogando:
                        lista_genomas[i].fitness -= 1
                        lista_genomas.pop(i)
                        redes.pop(i)
                if not cano.passou and passaro.x > cano.x:  # caso a posicao X do passaro for maior que a do cano, significa que o passaro passou
                    cano.passou = True
                    adicionar_cano = True
            cano.mover()
            if cano.x + cano.CANO_TOPO.get_width() < 0: # checa se o caso se encontra fora da tela
                remover_canos.append(cano)  # adiciona à lista de remoção

        if adicionar_cano:  # adiciona e remove os canos caso necessário
            pontuacao += 1
            canos.append(Cano(600))
            for genoma in lista_genomas:
                genoma.fitness += 5
        for cano in remover_canos:
            canos.remove(cano)

        for i, passaro in enumerate(passaros):
            if (passaro.y + passaro.imagem.get_height()) > chao.y or passaro.y < 0:
                passaros.pop(i)
                if ia_jogando:
                    lista_genomas.pop(i)
                    redes.pop(i)

        desenhar_tela(tela, passaros, canos, chao, pontuacao)

def rodar(diretorio_config):
    config = neat.config.Config(neat.DefaultGenome,
                                neat.DefaultReproduction,
                                neat.DefaultSpeciesSet,
                                neat.DefaultStagnation,
                                diretorio_config)

    populacao = neat.Population(config)
    populacao.add_reporter(neat.StdOutReporter(True))
    populacao.add_reporter(neat.StatisticsReporter())   # essas duas linhas nos trarão alguns dados de estatisticas no console, tais como em qual geração parou, etc.

    if ia_jogando:
        populacao.run(main, 50)   # o 2º parâmetro indica até qual numero de gerações a IA ficará tentando. Ao chegar no numero, o programa encerra. Caso nao quisermos um limite, basta deixar vazio.
    else:
        main(None, None)    # graças a implementação da IA, o main necessita de 2 parametro. Passando 2 parametros vazios aqui permitirá que um usuário jogue.

if __name__ == '__main__':  # permite a execução do arquivo caso esta for feita de forma manual apenas
    diretorio = os.path.dirname(__file__)
    diretorio_config = os.path.join(diretorio, 'config.txt') # importar a IA
    rodar(diretorio_config)