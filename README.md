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

O sub-projeto **NetPopulate** possui a seguinte estrutura de diretórios:

  - *lib* - contém arquivos que auxiliam o cálculo de rotas
  - *networks* - redes de tráfego usadas em testes do **NetPopulate**
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
    
O diretório onde foi feito checkout do **NetPopulate**
será chamado de <path_to_netpopulate> a partir daqui. 

### DemandKeeper

Trata-se de um utilitário que se conecta ao SUMO via TraCI e evita que
veículos saiam da simulação. Quando um veículo chega na sua edge de
destino, o DemandKeeper lhe atribui uma nova rota para que ele continue trafegando. 

Ele pode ser usado para gerenciar a demanda auxiliar de experimentos com o SUMO.
Nesse caso, o TraciHub deve ser chamado e a ele deverão se conectar o
script principal do experimento e o DemandKeeper. 

#### Funcionamento e uso

Assume-se que o usuário está familiarizado com o SUMO e sua arquitetura TraCI.

O DemandKeeper se conecta ao SUMO via TraCI e previne que os
veículos saiam da simulação. Quando qualquer veículo chega em sua edge
de destino, o DemandKeeper calcula um novo destino e rota para este veículo,
de modo que ele continue trafegando.

Para usar o DemandKeeper em conjunto com algum experimento do SUMO,
o TraciHub deve ser usado. Assim, o DemandKeeper e o script principal
do experimento se conectam ao TraciHub.

Atualmente, o DemandKeeper re-roteia qualquer veículo da simulação.
Isto pode ser inconveniente caso se queira que alguns veículos terminem
suas viagens de fato. Nesse caso, o DemandKeeper deve ser estendido para
que essa característica seja adicionada.

Assumindo que o SUMO tenha sido chamado com algum arquivo .rou.xml e aguarda a
conexão TraCI na porta <PORT>, o DemandKeeper deve ser executado da seguinte forma,
a partir do diretório <path_to_netpopulate>/src: 

    $ python demandKeeper.py -n network.net.xml -p <PORT> -b BEGIN -e END

Onde os parametros são:

    -n,--net-file:         arquivo .net.xml da rede de tráfego usada na simulação
    -p,--port:             número da porta da conexão via TraCI
    -b,--begin: (opcional) se informado, indicará a partir de qual timestep o DemandKeeper deve atuar
    -e,--end:   (opcional) se informado, indicará até qual timestep o DemandKeeper deve atuar 



### LoadKeeper

Trata-se de um utilitário que se conecta ao SUMO via TraCI e mantém
o número de veículos durante a simulação. Quando um veículo é removido
da simulação, o LoadKeeper insere outro. Os veículos inseridos são armazenados
e ao final um arquivo .rou.xml é gerado e pode ser carregado no SUMO como demanda auxiliar. 

#### Funcionamento e uso

Assume-se que o usuário está familiarizado com
o SUMO e sua arquitetura TraCI.

O LoadKeeper se conecta ao SUMO via TraCI e mantém o número de veículos
durante a simulação. Quando um veículo é removido normalmente da simulação,
o LoadKeeper insere outro com origem e destino aleatórios.

É possível fazer o LoadKeeper ignorar a saída de alguns veículos,
controlando apenas um conjunto específico. Isso é útil para evitar que
um veículo da demanda principal seja reinserido, de modo que apenas a demanda auxiliar seja controlada.

Para usar o LoadKeeper, o seguinte comando deve ser executado
no diretório <path_to_netpopulate>/src, assumindo-se que o SUMO está
carregando um arquivo .rou.xml qualquer e espera uma conexão vai TraCI na porta <PORT>:

    $ python loadkeeper.py [parametros]

Onde os parametros são:

    -h, --help:                           exibe todos os parâmetros aceitos pelo LoadKeeper.
    -n NETFILE, --net-file=NETFILE:       arquivo .net.xml com a rede de tráfego onde a demanda será controlada
    -r ROUTEFILE, --route-file=ROUTEFILE: arquivo .rou.xml a ser gerado com os veículos que o LoadKeeper inseriu durante sua execução.
    -b BEGIN, --begin=BEGIN:              timestep de início da atuação do LoadKeeper
    -e END, --end=END:                    timestep de fim da atuação do LoadKeeper
    -p PORT, --port=PORT:                 porta da conexão via TraCI
    -x EXCLUDE, --exclude=EXCLUDE:        não reinsere veículos cujos ID's tenham o prefixo EXCLUDE. 

O LoadKeeper pode ser usado antes ou em paralelo ao experimento que
necessita de demanda auxiliar. Os dois modos de funcionamento são descritos a seguir: 

##### Modo pré-experimento

Nesse modo, o usuário deverá planejar antes quantos timesteps o experimento
deve durar e o LoadKeeper deve ser executado nesse intervalo.
O SUMO deve ser executado carregando um arquivo .rou.xml com os veículos
que compõem a demanda auxiliar e em segunda o LoadKeeper deve ser chamado.

O LoadKeeper então controlará a reinserção dos veículos na rede.
Ele armazena os veículos e os timesteps em que eles são inseridos.
Ao final da execução, um arquivo .rou.xml é gerado com esses dados.
Esse arquivo reproduz a carga que o LoadKeeper controlou e pode ser
usado como a demanda auxiliar de experimentos com o SUMO.

A chamada do LoadKeeper nesse modo obedece à sintaxe apresentada na seção **Funcionamento e uso**. 

##### Em paralelo ao experimento

Nesse modo, o LoadKeeper e o experimento que terá a demanda
auxiliar controlada deve ser executados ao mesmo tempo. Isto pode ser
feito via TraciHub ou o usuário pode usar a classe do LoadKeeper dentro
do seu experimento.

#### TraciHub

Estando o SUMO aberto com um arquivo .rou.xml com a demanda auxiliar
e conectado ao TraciHub que aguarda a conexão do LoadKeeper, ele deve
ser executado de acordo com a sintaxe definida na seção **Funcionamento e uso**.

#### Instanciação da classe

O LoadKeeper pode ser importado para seu projeto de experimentos em IVC.
Para usá-lo, um objeto do tipo LoadKeeper deverá ser criado e, a cada timestep,
seu método act() deve ser chamado. Ao final, se for necessário escrever o
arquivo .rou.xml que o LoadKeeper inseriu na simulação,
o método writeOutput() deverá ser chamado. O uso desses métodos é descrito a seguir:

    Construtora do LoadKeeper: 

loadkeeper = LoadKeeper(net, outputFile = None, exclude = None)

Onde net é o objeto sumolib.net.Net que representa a rede de tráfego,
outputFile é o arquivo .rou.xml que pode ser gerado ao final e exclude
é o prefixo dos veículos que não são reinseridos
(ver parâmetro -x da chamada na seção **Funcionamento e uso**.

  - Método act()
  
        loadkeeper.act()

Basta executar este método a cada timestep.
O objeto LoadKeeper irá checar quais veículos
foram removidos e irá reinseri-los,
caso não tenham o prefixo definido em **exclude**.

  - Escrevendo o arquivo de saída: 

        loadkeeper.writeOutput()

Ao final da simulação, basta chamar esse método para gerar
o arquivo .rou.xml que terá todos os veículos que o LoadKeeper
inseriu durante a simulação. 

### ODPopulator

#### ODKeeper

Trata-se de um utilitário semelhante ao LoadKeeper,
mas que insere veículos na simulação de acordo com as
viagens determinadas em matriz OD. Os veículos inseridos são
armazenados e ao final um arquivo .rou.xml é gerado e
pode ser carregado no SUMO como demanda auxiliar. 

##### Funcionamento e uso

Assume-se que o usuário está familiarizado com o SUMO e sua arquitetura TraCI.

O VehicleEmitter recebe como entrada um arquivo xml com as definições
dos emissores de veículos, se conecta ao SUMO via TraCI e emite veículos
de acordo com as definições do arquivo de entrada.

O arquivo de definição de emissores tem a seguinte estrutura:

    <emitters>
        <!-- single-edge emitters -->
        <emitter laneId="e1_0" start="0" end="150" interval="10" />
        <emitter laneId="e1_1" start="5" interval="10" />
        ...

        <!-- routed vehicle emitters -->
        <emitter laneId="e1_1" arrivalEdge="e2" start="5" interval="10" />
        <emitter laneId="e2_0" arrivalEdge="e3" start="0" interval="10" />
        ...
    </emitters>

Os atributos da tag emitter são descritos a seguir:

  - **laneId**: é o ID da lane (não da edge) onde o emissor irá gerar veículos
  - **start**: (default=0) em qual timestep o emissor começará a atuar
  - **end**: (default=0) em qual timestep a emissão deve parar
  - **interval**: de quantos em quantos timesteps um veículo deve ser emitido
  - **arrivalEdge**: (opcional) se omitido, o veículo termina a viagem na
                 mesma edge onde foi criado. Se fornecido, uma rota é
                 calculada até a edge de destino e o veículo vai até ela. 


Para executar o Emitter, o seguinte comando deve ser
executado no diretório <path_to_netpopulate>/src,
assumindo-se que o SUMO espera uma conexão vai TraCI na porta <PORT>:

    $ python main.py [parametros]

Onde os parametros são:

    -h, --help:                     exibe todos os parâmetros aceitos pelo LoadKeeper.
    -n NETFILE, --net-file=NETFILE: arquivo .net.xml com a rede de tráfego onde o emissor atuará
    --emitters-input=EMITTERSINPUT: arquivo .xml de definição dos emissores
    -p PORT, --port=PORT:           porta da conexão via TraCI 

Opções de logging:

    --log.level=LOGLEVEL: (opcional) nível de detalhe das mensagens registradas, pode ser DEBUG, INFO, WARNING, ERROR or CRITICAL [default: INFO]
    --log.file=FILE:      (opcional) arquivo onde as mensagens de log serão escritas
    --log.stdout:         (opcional, ativado por padrão) escrever as mensagens de log no stream de saída padrão a.k.a. o terminal.
    --log.stderr:         (opcional) escrever as mensagens de log no stream de erros padrão 

Para que o Emitter seja executado em paralelo a algum experimento,
o TraciHub deve ser executado, conectando-se a ele o Emitter, o script
do experimento e o SUMO. 

#### ODLoader

Trata-se de um utilitário que se conecta ao SUMO via TraCI e
adiciona veículos à simulação até a carga desejada ser atingida.
As origens e destinos dos veículos inseridos são determinadas
de acordo com uma matriz OD. O ODLoader registra quando um veículo entra
na simulação e então gera um .rou.xml com os dados dos veículos que entraram.

##### Funcionamento e uso

Assume-se que o usuário está familiarizado
com o SUMO e sua arquitetura TraCI.

O ODLoader se conecta ao SUMO via TraCI e insere veículos na rede
viária até se atingir a carga desejada. É possível configurar uma duração
na qual o ODLoader mantém a carga desejada na rede.

Para usar o ODLoader, o seguinte comando deve ser executado no
diretório <path_to_netpopulate>/src/odpopulator, assumindo-se que
o SUMO espera uma conexão vai TraCI na porta <PORT>:

    $ python odloader.py [parametros]

Onde os parametros são:

    -h, --help:                               exibe todos os parâmetros aceitos pelo ODLoader.
    -n NETFILE, --net-file=NETFILE:           arquivo .net.xml com a rede de tráfego onde a demanda será controlada
    -t TAZFILE, --taz-file=TAZFILE:           arquivo .taz.xml com a definição dos distritos da rede viária
    -m ODMFILE, --odm-file=ODMFILE:           arquivo com a matriz OD, i.e., as definições das viagens entre os distritos
    -l MAX_PER_TS, --limit-per-ts=MAX_PER_TS: número máximo de veículos a ser inserido na simulação a cada timestep
    -o OUTPUT, --output=OUTPUT:               arquivo .rou.xml com os veículos inseridos na simulação
    -d NUMVEH, --driver-number=NUMVEH:        número máximo de veículos ao mesmo tempo na rede de tráfego
    -b BEGIN, --begin=BEGIN:                  timestep de início da atuação do ODLoader
    -e END, --end=END:                        timestep de fim da atuação do ODLoader
    --duration=DURATION:                      número de timesteps no qual a rede deve ser mantida com a carga desejada
    -p PORT, --port=PORT:                     porta da conexão via TraCI
    -u, --uniform:                            usar distribuição uniforme sobre as origens e destinos ao invés da matriz OD
    -s STEADYOUT, --steady-output=STEADYOUT:  (opcional) arquivo que conterá #timestep vs. número de viagens completadas enquanto a rede está com a carga desejada 

### VehicleEmitter

Trata-se de um utilitário que se conecta ao SUMO via TraCI e
cria veículos de tempos em tempos em determinadas edges da rede de tráfego.

O VehicleEmitter recebe como entrada um arquivo xml com as definições dos
emissores de veículos, se conecta ao SUMO via TraCI e emite veículos de
acordo com as definições do arquivo de entrada.

O arquivo de definição de emissores tem a seguinte estrutura:

    <emitters>
        <!-- single-edge emitters -->
        <emitter laneId="e1_0" start="0" end="150" interval="10" />
        <emitter laneId="e1_1" start="5" interval="10" />
        ...

        <!-- routed vehicle emitters -->
        <emitter laneId="e1_1" arrivalEdge="e2" start="5" interval="10" />
        <emitter laneId="e2_0" arrivalEdge="e3" start="0" interval="10" />
        ...
    </emitters>

Os atributos da tag **emitter** são descritos a seguir:

  - **laneId**: é o ID da lane (não da edge) onde o emissor irá gerar veículos
  - **start**: (default=0) em qual timestep o emissor começará a atuar
  - **end**: (default=0) em qual timestep a emissão deve parar
  - **interval**: de quantos em quantos timesteps um veículo deve ser emitido
  - **arrivalEdge**: (opcional) se omitido, o veículo termina a viagem na
                     mesma edge onde foi criado. Se fornecido, uma rota é calculada até a
                     edge de destino e o veículo vai até ela. 

Para executar o Emitter, o seguinte comando deve ser
executado no diretório <path_to_netpopulate>/src, assumindo-se que o SUMO
espera uma conexão vai TraCI na porta <PORT>:

    $ python main.py [parametros]

Onde os parametros são:

    -h, --help:                     exibe todos os parâmetros aceitos pelo LoadKeeper.
    -n NETFILE, --net-file=NETFILE: arquivo .net.xml com a rede de tráfego onde o emissor atuará
    --emitters-input=EMITTERSINPUT: arquivo .xml de definição dos emissores
    -p PORT, --port=PORT:           porta da conexão via TraCI 

Opções de logging:

        --log.level=LOGLEVEL: (opcional) nível de detalhe das mensagens registradas, pode ser DEBUG, INFO, WARNING, ERROR or CRITICAL [default: INFO]
        --log.file=FILE:      (opcional) arquivo onde as mensagens de log serão escritas
        --log.stdout:         (opcional, ativado por padrão) escrever as mensagens de log no stream de saída padrão a.k.a. o terminal.
        --log.stderr:         (opcional) escrever as mensagens de log no stream de erros padrão 

Para que o Emitter seja executado em paralelo a algum experimento,
o TraciHub deve ser executado, conectando-se a ele o Emitter, o script do experimento e o SUMO. 












