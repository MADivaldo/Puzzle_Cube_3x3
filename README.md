# Cubo 3x3 – Puzzle Interativo

Protótipo interativo de manipulação de um cubo 3x3 rotacional, desenvolvido inicialmente em Python + Pygame.

O sistema permite navegar entre peças da face atual e realizar rotações de linhas, colunas e faces do cubo em um ambiente tridimensional interativo.

---

# Conceito

O cubo funciona como um objeto tridimensional manipulável.

Cada face possui uma cor única:

| Face     | Cor      |
| -------- | -------- |
| Frente   | Amarelo  |
| Trás     | Branco   |
| Direita  | Azul     |
| Esquerda | Laranja  |
| Topo     | Verde    |
| Base     | Vermelho |

O sistema permite:

* Navegação entre peças
* Troca de face ao alcançar extremidades
* Rotação de linhas
* Rotação de colunas
* Rotação da face frontal
* Rotação visual livre do preview
* Aleatorização e reset do cubo

---

# Controles

## Navegação

| Tecla   | Ação                        |
| ------- | --------------------------- |
| W A S D | Move seleção entre peças    |
| Bordas  | Troca para a face adjacente |

---

## Visualização

| Controle      | Ação                           |
| ------------- | ------------------------------ |
| Click + Mouse | Rotaciona visualmente o cubo   |
| F             | Centraliza/alinha a face atual |

---

## Manipulação

| Controle | Ação                             |
| -------- | -------------------------------- |
| Espaço   | Fixa/libera peça selecionada     |
| W / S    | Gira coluna para cima/baixo      |
| A / D    | Gira linha para esquerda/direita |
| Q / E    | Gira face anti-horário/horário   |

---

## Utilidades

| Controle      | Ação                     |
| ------------- | ------------------------ |
| R             | Aleatoriza o cubo        |
| Botão Resetar | Volta ao estado original |

---

# Estrutura do Sistema

O cubo utiliza um modelo interno baseado em:

* Stickers
* Posições 3D reais
* Normais de face
* Rotação por slices/fatias

Cada sticker possui:

* Cor
* Face original
* Posição no espaço
* Normal da superfície

As rotações acontecem através de transformações vetoriais 3D reais.

---

# Tecnologias

## Versão Desktop

* Python 3.12
* Pygame

## Versão Web (planejada)

* HTML
* JavaScript
* Three.js

---

# Como Executar

# Instalar Python 3.12

Caso o Python não esteja instalado, primeiro instale o installer oficial do Python para Windows:

[Python Download Windows](https://www.python.org/downloads/windows/?utm_source=chatgpt.com)

Durante a instalação:

* Marque a opção:

```text id="pq3sqx"
Add Python to PATH
```

* Clique em:

```text id="0b2js5"
Install Now
```

---

## Instalar Python 3.12.10 pelo terminal

Após instalar o Python e abrir novamente o terminal:

```bash id="0kqmbf"
winget install Python.Python.3.12 --version 3.12.10
```

---

## Verificar instalação

```bash id="0xf53f"
python --version
```

Resultado esperado:

```text id="8c2kvf"
Python 3.12.10
```

---

## Instalar dependências

```bash id="s6qv34"
python -m pip install pygame
```

---

## Abrir terminal na pasta do projeto (Windows)

1. Vá até a pasta onde está o arquivo `.py`
2. Segure `Shift`
3. Clique com botão direito em um espaço vazio
4. Clique em:

```text id="jvq26v"
Open in Terminal
```

ou

```text id="rvvv8q"
Abrir janela do PowerShell aqui
```

---

## Executar o projeto

```bash id="pxltcm"
python prototipo_cubo_3x3_artefato_v9.py
```

A janela do Pygame será aberta automaticamente executando o protótipo.

---

# Estrutura do Projeto

```text id="xjlwm4"
/
├── prototipo_cubo_3x3_artefato_v9.py
├── README.md
```

---

# Roadmap

## Próximos Passos

* [ ] Versão Web em HTML + Three.js
* [ ] Suporte a animações suaves
* [ ] Salvamento de estado
* [ ] Sons e feedbacks visuais
* [ ] Shader estilizado
* [ ] Compatibilidade com gamepad

---

# Objetivo de Design

O projeto foi pensado como um sistema de manipulação tridimensional inspirado em cubos mágicos e puzzles mecânicos.

O foco principal está em:

* Navegação entre faces
* Rotação de linhas e colunas
* Manipulação espacial
* Leitura visual do cubo
* Interação tridimensional

Inspirado em:

* Cubo mágico
* Puzzles mecânicos tridimensionais
* Objetos manipuláveis
* Interfaces espaciais interativas

---

# Licença

Protótipo experimental desenvolvido para estudo e integração em projetos de jogos.
