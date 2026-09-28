# Diagramas Ternários

[English](README.md) | [Português (Brasil)](README.pt-BR.md)

Aplicativo desktop em Python para plotagem de diagramas ternários de fases com
uma região monofásica (1F) e uma região bifásica (2F) separadas por uma curva
de separação ajustada aos dados.

## Requisitos

- Python 3.9 ou superior
- Tkinter (em algumas distribuições Linux, instale `python3-tk`)
- NumPy, SciPy e Matplotlib

Instale as dependências Python:

```bash
python -m pip install -r requirements.txt
```

## Executar

```bash
python ternary_gui.py
```

O idioma da interface é escolhido na caixa **Language / Idioma** (`pt` ou `en`);
todos os rótulos são atualizados imediatamente.

## Dados de entrada

Informe os nomes dos três componentes separados por vírgulas (`A, B, C` por
padrão). Cada linha dos dados contém a fração molar de A, a fração molar de B e
a classificação experimental `1F` ou `2F`. A fração restante é calculada por:

`Xc = 1 − (Xa + Xb)`

Regras dos dados:

- cada fração deve estar entre 0 e 1, e `Xa + Xb` não pode exceder 1;
- vírgula, ponto e vírgula e espaço são aceitos como separadores;
- linhas iniciadas com `#` são ignoradas;
- o campo **Número de pontos** deve corresponder às linhas preenchidas;
- são exigidos pelo menos 3 pontos válidos, sendo pelo menos 2 pontos `2F` com
  frações de A diferentes.

### Exemplo

```text
0.70, 0.15, 1F
0.62, 0.30, 1F
0.55, 0.20, 1F
0.05, 0.10, 2F
0.10, 0.45, 2F
0.08, 0.80, 2F
0.20, 0.25, 2F
0.18, 0.65, 2F
```

## Curva de separação

A curva é ajustada **apenas aos pontos 2F**:

1. os pontos 2F são ordenados pela posição horizontal no triângulo;
2. para cada abscissa vale o ponto 2F mais alto, de modo que nenhum ponto 2F
   fique acima da curva;
3. uma spline PCHIP (monotônica por trecho) liga esses pontos sem ondulação e
   passa exatamente por eles;
4. fora do intervalo dos pontos, a curva segue a tangente da extremidade
   correspondente até as bordas do triângulo.

A classificação segue a curva: **abaixo da curva a fase é 2F e acima é 1F**.
Como a PCHIP não ultrapassa os pontos, todos os pontos 2F ficam exatamente sobre
a fronteira e nenhum deles é pintado como 1F; os pontos 1F são desenhados, mas
não entram no ajuste. A forma da curva depende da distribuição dos pontos 2F,
portanto medições próximas à fronteira refinam o resultado.

## O gráfico

**Gerar gráfico** desenha o diagrama ternário de fases clássico:

- triângulo equilátero com moldura preta e as duas regiões preenchidas em tons
  de cinza;
- percentuais de 10 a 90 na base (fração de B), na borda direita (fração de A) e
  na borda esquerda (fração de C);
- grade tracejada de 10 em 10 %, com uma família de paralelas para cada fração
  unindo as bordas do triângulo, como um papel isométrico;
- nome de cada componente no seu vértice e título `A - B - C` acima do triângulo;
- rótulo de cada fase (`1-fase` / `2-fase`) dentro da região correspondente;
- legenda com amostras de cor posicionada à esquerda, fora do triângulo;
- os pontos medidos são desenhados como círculos na cor da sua fase e a curva de
  separação como uma linha preta no estilo escolhido.

**Salvar gráfico** exporta a figura atual para PNG, JPEG, SVG ou PostScript. A
barra de ferramentas permite zoom e navegação, e **About** apresenta versão,
autor, data e instituições de vínculo.

As cores das duas regiões e o estilo de linha da curva podem ser alterados no
grupo **Aparência**.

## Arquivos do projeto

| Arquivo | Descrição |
| --- | --- |
| `ternary_gui.py` | Aplicativo: interface, validação dos dados, ajuste da curva e plotagem |
| `requirements.txt` | Dependências Python |
| `README.md` / `README.pt-BR.md` | Esta documentação (inglês / português do Brasil) |
| `ternary-plot-phase-diagram.png` | Imagem usada como referência para o layout |

## Sobre

- Versão 1.0.0
- Autor: Dr. Arlan da Silva Gonçalves
- Instituto Federal de Educação, Ciência e Tecnologia do Espírito Santo –
  Campus Vila Velha / Campus Vitória
- Universidade Federal do Espírito Santo – PPGQ / UFES
