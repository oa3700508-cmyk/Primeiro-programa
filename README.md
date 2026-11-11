import math
import random
import pygame
from pygame.math import Vector2 as V

LARGURA, ALTURA = 800, 600
RAIO_JOGADOR, VEL_JOGADOR = 14, 4.2
VEL_BALA, CADENCIA = 12, 150  # cadência = ms entre tiros

TIPOS = {
    "normal": dict(r=12, vel=1.6, hp=1, pts=10, dano=20, cor=(220, 70, 70)),
    "rapido": dict(r=8, vel=3.0, hp=1, pts=15, dano=20, cor=(250, 170, 50)),
    "tanque": dict(r=20, vel=0.9, hp=5, pts=40, dano=35, cor=(150, 80, 210)),
}


def novo_inimigo(nivel):
    lado = random.choice("NSLO")
    if lado == "N":
        p = (random.uniform(0, LARGURA), -30)
    elif lado == "S":
        p = (random.uniform(0, LARGURA), ALTURA + 30)
    elif lado == "L":
        p = (LARGURA + 30, random.uniform(0, ALTURA))
    else:
        p = (-30, random.uniform(0, ALTURA))
    tipo = random.choices(list(TIPOS), weights=[70, 15 + 2 * nivel, 5 + 2 * nivel])[0]
    d = TIPOS[tipo]
    return {"pos": V(p), "tipo": tipo, "hp": d["hp"], "vel": d["vel"] * (1 + 0.04 * nivel)}


def explodir(particulas, pos, cor, n=12):
    for _ in range(n):
        ang, v = random.uniform(0, 2 * math.pi), random.uniform(1, 4)
        particulas.append({"pos": V(pos), "vel": V(math.cos(ang), math.sin(ang)) * v, "vida": 22, "cor": cor})


def jogar(tela, relogio, fonte):
    pos, hp, pontos, nivel = V(LARGURA / 2, ALTURA / 2), 100, 0, 1
    balas, inimigos, itens, particulas = [], [], [], []
    ultimo_tiro, inv_ate, spawn_timer, dt = 0, 0, 0, 16

    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                return pontos, False
        agora = pygame.time.get_ticks()
        teclas = pygame.key.get_pressed()
        mouse = V(pygame.mouse.get_pos())

        # --- jogador: movimento (WASD/setas) e mira (mouse) ---
        mov = V((teclas[pygame.K_d] or teclas[pygame.K_RIGHT]) - (teclas[pygame.K_a] or teclas[pygame.K_LEFT]),
                (teclas[pygame.K_s] or teclas[pygame.K_DOWN]) - (teclas[pygame.K_w] or teclas[pygame.K_UP]))
        if mov.length() > 0:
            pos += mov.normalize() * VEL_JOGADOR
        pos.x = max(RAIO_JOGADOR, min(LARGURA - RAIO_JOGADOR, pos.x))
        pos.y = max(RAIO_JOGADOR, min(ALTURA - RAIO_JOGADOR, pos.y))
        mira = mouse - pos
        direcao = mira.normalize() if mira.length() > 0 else V(1, 0)

        if (pygame.mouse.get_pressed()[0] or teclas[pygame.K_SPACE]) and agora - ultimo_tiro > CADENCIA:
            balas.append({"pos": pos + direcao * 20, "vel": direcao * VEL_BALA})
            ultimo_tiro = agora

        # --- balas: movimento e acertos ---
        vivas = []
        for b in balas:
            b["pos"] += b["vel"]
            if not (0 <= b["pos"].x <= LARGURA and 0 <= b["pos"].y <= ALTURA):
                continue
            alvo = next((e for e in inimigos if b["pos"].distance_to(e["pos"]) < TIPOS[e["tipo"]]["r"] + 3), None)
            if alvo:
                alvo["hp"] -= 1
                explodir(particulas, b["pos"], TIPOS[alvo["tipo"]]["cor"], 3)
            else:
                vivas.append(b)
        balas = vivas

        # --- inimigos: spawn, perseguição, morte ---
        spawn_timer += dt
        if spawn_timer > max(250, 1000 - nivel * 70):
            spawn_timer = 0
            inimigos.append(novo_inimigo(nivel))
        for e in inimigos:
            d = pos - e["pos"]
            if d.length() > 0:
                e["pos"] += d.normalize() * e["vel"]
        for e in [e for e in inimigos if e["hp"] <= 0]:
            pontos += TIPOS[e["tipo"]]["pts"]
            explodir(particulas, e["pos"], TIPOS[e["tipo"]]["cor"])
            if random.random() < 0.12:
                itens.append({"pos": V(e["pos"]), "t0": agora})
        inimigos = [e for e in inimigos if e["hp"] > 0]
        nivel = 1 + pontos // 150

        # --- contato com o jogador ---
        restantes = []
        for e in inimigos:
            if e["pos"].distance_to(pos) < TIPOS[e["tipo"]]["r"] + RAIO_JOGADOR:
                if agora > inv_ate:
                    hp -= TIPOS[e["tipo"]]["dano"]
                    inv_ate = agora + 600
                explodir(particulas, e["pos"], TIPOS[e["tipo"]]["cor"])
            else:
                restantes.append(e)
        inimigos = restantes
        if hp <= 0:
            return pontos, True

        # --- itens de cura ---
        itens = [i for i in itens if agora - i["t0"] < 8000]
        for i in itens[:]:
            if i["pos"].distance_to(pos) < 20:
                hp = min(100, hp + 25)
                itens.remove(i)
        for p in particulas:
            p["pos"] += p["vel"]
            p["vida"] -= 1
        particulas = [p for p in particulas if p["vida"] > 0]

        # --- desenho ---
        tela.fill((18, 20, 32))
        for x in range(0, LARGURA, 40):
            pygame.draw.line(tela, (28, 31, 48), (x, 0), (x, ALTURA))
        for y in range(0, ALTURA, 40):
            pygame.draw.line(tela, (28, 31, 48), (0, y), (LARGURA, y))
        for i in itens:
            c = (int(i["pos"].x), int(i["pos"].y))
            pygame.draw.circle(tela, (60, 200, 100), c, 11)
            pygame.draw.rect(tela, (255, 255, 255), (c[0] - 6, c[1] - 2, 12, 4))
            pygame.draw.rect(tela, (255, 255, 255), (c[0] - 2, c[1] - 6, 4, 12))
        for p in particulas:
            pygame.draw.circle(tela, p["cor"], (int(p["pos"].x), int(p["pos"].y)), max(1, p["vida"] // 7))
        for e in inimigos:
            d = TIPOS[e["tipo"]]
            c = (int(e["pos"].x), int(e["pos"].y))
            pygame.draw.circle(tela, d["cor"], c, d["r"])
            pygame.draw.circle(tela, (20, 20, 30), c, d["r"], 2)
            if d["hp"] > 1:  # barra de vida dos tanques
                pygame.draw.rect(tela, (60, 20, 20), (c[0] - 16, c[1] - d["r"] - 9, 32, 4))
                pygame.draw.rect(tela, (80, 230, 100), (c[0] - 16, c[1] - d["r"] - 9, 32 * e["hp"] / d["hp"], 4))
        for b in balas:
            pygame.draw.circle(tela, (255, 240, 120), (int(b["pos"].x), int(b["pos"].y)), 4)
        if not (agora < inv_ate and (agora // 80) % 2):  # pisca ao tomar dano
            c = (int(pos.x), int(pos.y))
            pygame.draw.line(tela, (200, 200, 210), c, (pos + direcao * 24), 6)
            pygame.draw.circle(tela, (70, 150, 250), c, RAIO_JOGADOR)
            pygame.draw.circle(tela, (230, 240, 255), c, RAIO_JOGADOR, 2)
        m = (int(mouse.x), int(mouse.y))  # mira
        pygame.draw.circle(tela, (255, 255, 255), m, 9, 1)
        pygame.draw.line(tela, (255, 255, 255), (m[0] - 14, m[1]), (m[0] + 14, m[1]))
        pygame.draw.line(tela, (255, 255, 255), (m[0], m[1] - 14), (m[0], m[1] + 14))

        pygame.draw.rect(tela, (60, 30, 30), (10, 10, 200, 16))
        pygame.draw.rect(tela, (230 - hp * 2, min(255, 60 + hp * 2), 70), (10, 10, 2 * max(hp, 0), 16))
        pygame.draw.rect(tela, (240, 240, 240), (10, 10, 200, 16), 2)
        tela.blit(fonte.render(f"Pontos: {pontos}   Nivel: {nivel}", True, (240, 240, 240)), (10, 34))
        pygame.display.flip()
        dt = relogio.tick(60)


def tela_fim(tela, fonte, pontos):
    tela.fill((18, 20, 32))
    linhas = [f"Voce caiu! Pontos: {pontos}", "ENTER: jogar de novo   ESC: sair"]
    for i, texto in enumerate(linhas):
        img = fonte.render(texto, True, (240, 240, 240))
        tela.blit(img, img.get_rect(center=(LARGURA // 2, ALTURA // 2 + i * 36 - 18)))
    pygame.display.flip()

    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                return False
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_RETURN:
                    return True
                if e.key == pygame.K_ESCAPE:
                    return False


def main():
    pygame.init()
    tela = pygame.display.set_mode((LARGURA, ALTURA))
    pygame.display.set_caption("Tiro")
    relogio = pygame.time.Clock()
    fonte = pygame.font.SysFont(None, 28)

    while True:
        pygame.mouse.set_visible(False)  # usamos nossa própria mira
        pontos, continuar = jogar(tela, relogio, fonte)
        pygame.mouse.set_visible(True)
        if not continuar or not tela_fim(tela, fonte, pontos):
            break
    pygame.quit()


if __name__ == "__main__":
    main()