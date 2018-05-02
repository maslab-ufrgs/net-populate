# NetPopulate

O **NetPopulate** é um projeto que contém scripts diversos
para a geração e controle da demanda auxiliar em
experimentos usando o SUMO.  Atualmente
o NetPopulate é composto pelos seguintes utilitários (segue uma breve descrição):

  - **DemandKeeper**: mantém a carga na rede constante re-roteando os veículos que terminam suas viagens
  - **LoadKeeper**: mantém a carga na rede constante inserindo um novo veículo quando outro sai da rede
  - **ODPopulator**
    - **ODKeeper**: igual ao LoadKeeper, mas usa matriz OD ao invés de probabilidade uniforme
                    para selecionar as origens e destinos dos veículos inseridos
    - **ODLoader**: checa a cada timestep se a carga na rede é igual a desejada e insere veículos
                    na rede até atingi-la
  - **VehicleEmitter**: emite veículos em intervalos constantes de tempo

**ATENÇÃO**: os scripts do **NetPopulate** necessitam do interpretador
python instalado (ele foi testado no python 2.7.3). 

## Organização dos arquivos

O sub-projeto NetPopulate possui a seguinte estrutura de diretórios:

  - *lib* - contém arquivos que auxiliam o cálculo de rotas
  - *networks* - redes de tráfego usadas em testes do NetPopulate
  - *testnet* - rede simples com um cruzamento e ruas de uma faixa
  - *multilaneTestNet* - rede simples com um cruzamento e ruas de mais de uma faixa.
                         Também possui um arquivo de exemplo de definição de emissores para o VehicleEmitter. 
  - *src* - código fonte, explicado na seção que se segue. 

## Código fonte

Dentro do diretorio src, os seguintes arquivos são encontrados (agrupados por utilitário):

  - VehicleEmitter
    - *main.py* - é o script principal que deve ser
                chamado para uso do VehicleEmitter      
    - *application.py* - realiza o parsing dos parâmetros da linha de
                       comando e chama as classes do VehicleEmitter
    - *emitter.py* - contém as classes responsáveis por emitir os veículos e
                   analisar o arquivo de definição de emissores 
    
  - DemandKeeper
      - *demandKeeper.py* - responsável pela execução do DemandKeeper
      
  - LoadKeeper
      - *loadkeeper.py* - contém a classe LoadKeeper e também cuida da execução direta
                        do loadkeeper quando chamado na linha de comando
                        
    - ODPopulator - contém o ODKeeper e ODLoader,
                    além de módulos auxiliares para lidar com matrizes OD.
  - Outros
    - *populator.py* - não é mais utilizado. Insere veículos na rede em determinados timesteps
    - *rouLoader.py* - apenas carrega a demanda de um arquivo .rou.xml e a insere via TraCI no SUMO
    - *loadCounter.py* - monitora a rede de tráfego via TraCI e exibe a ocupação da edge com maior congestionamento 
    
### DemandKeeper

O VehicleEmitter faz parte do projeto **NetPopulate**.
Trata-se de um utilitário que se conecta ao SUMO via TraCI e
cria veículos de tempos em tempos em determinadas edges da rede de tráfego. 

### LoadKeeper

### ODPopulator

#### ODKeeper

#### ODLoader

### VehicleEmitter

