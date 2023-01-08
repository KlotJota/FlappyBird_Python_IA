import pygame   # necessário para o jogo
import os       # permite a integração com arquivos do computador
import random   # geração de numeros aleatórios para os obstáculos do jogo

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
    chao.desenhar(tela)

    pygame.display.update() # update na tela para a mesma ser desenhada

def main():
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
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_SPACE:
                    for passaro in passaros:
                        passaro.pular()

        # movimentação dos objetos
        for passaro in passaros:
            passaro.mover()
        chao.mover()

        adicionar_cano = False
        remover_canos = []

        for cano in canos:
            for posicao, passaro in enumerate(passaros):
                if cano.colidir(passaro):
                    passaros.pop(posicao)
                    main()
                if not cano.passou and passaro.x > cano.x:  # caso a posicao X do passaro for maior que a do cano, significa que o passaro passou
                    cano.passou = True
                    adicionar_cano = True
            cano.mover()
            if cano.x + cano.CANO_TOPO.get_width() < 0: # checa se o caso se encontra fora da tela
                remover_canos.append(cano)  # adiciona à lista de remoção

        if adicionar_cano:  # adiciona e remove os canos caso necessário
            pontuacao += 1
            canos.append(Cano(600))
        for cano in remover_canos:
            canos.remove(cano)

        for posicao, passaro in enumerate(passaros):
            if (passaro.y + passaro.imagem.get_height()) > chao.y or passaro.y < 0:
                passaros.pop(posicao)
                main()

        desenhar_tela(tela, passaros, canos, chao, pontuacao)

if __name__ == '__main__':  # permite a execução do arquivo caso esta for feita de forma manual apenas
    main()