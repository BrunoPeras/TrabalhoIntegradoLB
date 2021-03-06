#Metodologia Desenvolvida durante a realização do trabalho da unidade curricular de Laboratórios de Bioinformática
#em conjunto com Biologia de Sistemas e Algoritmos para Análise de Sequências Biológicas

#Imports
from Bio import SeqIO
from Bio import Entrez
from Bio.Blast import NCBIWWW,NCBIXML
from Bio import AlignIO
from Bio import Phylo

################################################
#1ºobjetivo, retirar o genoma completo do NCBI
################################################

Entrez.email = "pereirinha_bp@hotmail.com" #indicar sempre o e-mail para aceder ao NCBI

procura = Entrez.esearch(db="nucleotide", term="Pseudomonas aeruginosa[Organism] AND complete genome[title] AND PAO1[strain]
print(procura) #possível observar que se encontra num formato para ser lido por funções de input/output ("TextIOWrapper")

procura_lida = Entrez.read(procura)
print(procura_lida) #dicionário com o resultado da nossa procura no Entrez

lista_id = procura_lida["IdList"] # chave do dicionário que nos indica os id's encontrados tendo em conta a query
print(lista_id) 

info_id = [] #colocar numa lista a informação referente a cada um dos id, informação obtida é necessário ser lida
for i in lista_id:
  indo_id.append(Entrez.efetch(db="nucleotide",rettype="gbwithparts", retmode="text",id=i) #agradecimento ao Tiago Oliveira do nosso mestrado por nos ter ajudado com o rettype para que se pudesse obter o genoma com as features todas

#ler ambos os ficheiros
handle0 = SeqIO.read(info_id[0],"genbank")
handle1 = SeqIO.read(info_id[1],"genbank") #ao executar este comando é obtido um erro porque a informação não é completamente lida o que nos levou a crer que este id não seria o correto
                                           #por via de dúvidas consultamos os dados do primeiro
#id do genoma e descrição
print(handle0.id)
print(handle0.description)
#confirmar o número de features do nosso genoma para garantir que temos a informação toda
print(len(handle0.features)) #Output:11908

#primeiro objetivo concluído
record = handle0

#########################
#Dados acerca do genoma
#########################

#id genoma
print(record.id)

#descrição do genoma
print(record.description)

#Anotações
print(record.annotations) #dicionário onde é possível retirar a taxonomia, tipo de molécula, o organismo de origem, as referências, ...

#Obter duas listas, uma com os índices de genes e outra com os dos CDS's
genes = []
CDS = []
for i in range(len(record.features)):
  if record.features[i].type == "CDS":
    CDS.append(i)
  elif record.features[i].type == "gene":
    genes.append(i)

#Número de genes e CDS's
print(len(genes))
print(len(CDS))

#############################################
#Determinar os genes essenciais do organismo
#############################################
#Obter o ficheiro OGEE com dados referentes aos genes essenciais ou não do nosso organismo, guardar o ficheiro, que após o download é preciso converter em ficheiro txt separado por tabulações

#função que recebe um ficheiro(da base de dados OGEE, convertido de excel para txt separado por tabulações) e retorna uma lista com os genes essenciais
def essenciality(ficheiro):
    try:
        file = open(ficheiro,"r")
        lista_genes_essenciais = []
        file.readline()
        for line in file:
            linha = line.rstrip().split("\t")
            tuplo = linha[0]
            palavras = tuplo.split(",")
            if palavras[-1]=="Essential":
                lista_genes_essenciais.append(palavras[0])
        file.close()
        return lista_genes_essenciais
    except FileNotFoundError:
        print("Ficheiro não encontrado")
    except:
        print("Erro:")
        raise
 genes_essenciais = essenciality(<nome_ficheiro>) #no nosso caso era:"Pseudomonas-aeruginosa-PAO1_consolidated.txt"
 #número de genes essenciais
 print(len(genes_essenciais))
 
#função que retira os genes essenciais do conjunto de genes das features, retorna lista dos indices dos genes essenciais nas features
#::param lista_indices, lista_genes, record:: uma lista com os indices de todos os genes nas features, uma lista com os genes essenciais da OGEE e o record que contempla as features
def essential_genes_feat(lista_indices, lista_locus, record):
    l_essfeat = []
    for i in lista_indices:
        dict = record.features[i].qualifiers
        locus = dict['locus_tag'][0]
        if locus in lista_locus:
            l_essfeat.append(i)
    return l_essfeat

ind_essgenes = essential_genes_feat(genes,genes_essenciais,record)

print(len(ind_essgenes)) #confirmar o tamanho --> Output: 336 genes essenciais

#############################
#BLAST dos genes essenciais
#############################
#Nota: decidimos só fazer BLAST dos genes essenciais pois a totalidade dos genes era incomportável em termos de cronológicos pois o tempo que demorava a fazer BLAST de 5000 e tal genes era demasiado (75 genes por 6horas)

#1ºcriar um dicionário em que as chaves são o nome dos genes e os valores a sequência correspondente

#função que retira do genoma completo as sequencias de nucleotidos de features e retorna um dicionário em que a chave é o elemento da categoria da feature e o value é a sequencia de DNA
#::param record, lista_ind, lista_chaves:: record é a variável que armazena o objeto Seq.Record e a lista é uma lista de indices com as features de interesse, e a lista_chaves é uma lista com as chaves do futuro dicionário
def retira_seq_features(record, lista_ind, lista_chaves):
    d = {}
    for i in range(len(lista_ind)):
        feat = record.features[lista_ind[i]]
        sequencia = feat.extract(record.seq)
        categoria = lista_chaves[i]
        d[categoria] = sequencia
    return d
    
   
d_essenciais = retira_seq_features(record,ind_essgenes, genes_essenciais)
print(len(d_essenciais))#quantidade de genes essenciais para confirmar

#2ºcorrer para cada sequência um blast e verificar se não é homólogo, isto é, não foi realizado nenhum alinhamento

#função que leva como argumento um dicionario em que as chaves sao id's dos genes e os values são as sequencias desses genes
#devolve um dicionario com as mesmas chaves e o resultado do blast, sendo que contem apenas as sequencias para as quais não se encontrou alinhamentos após blast
def dic_genesnaohomologos(dicionario):
    d = {}
    for key in dicionario:
        result = NCBIWWW.qblast("blastn","human_genomic",str(dicionario[key]))
        blast_result = NCBIXML.read(result)
        if blast_result.alignments == []:
            d[key] = blast_result
    return d
            
nao_homologos = dic_genesnaohomologos(d_essenciais)

#Escrever num ficheiro os genes não homólogos
file = open("genes_essenciais_nao_homologos.txt","w")
for key in dessenc_n_homologos:
    file.write(key+"\n")
file.close()
 
######################
#Seleção dos 3 genes
######################

#A primeira seleção (gene essencial com droga conhecida), foi feita através de uma pesquisa na base de dados DrugBank submetendo uma query
#com Pseudomonas aeroginosa PAO1, sendo que se selecionou uma droga que tinha como alvo uma proteína deste organismo. Para ver qual a correspondência
#ao gene, foi inserida na base de dados KEGG essa proteína. Após obter o gene, confirmou-se que era essencial e não homólogo, através da verificação 
#desse gene no dicionário <nao_homologos>. Resultado: PA4418.

#Os dois outros genes foram escolhidos aleatoriamente do dicionário. Selecionávamos um e íamos verificar na base de dados DrugBank se exitia 
#ou não uma droga. Decidimos escolher um com uma droga, mas que a droga para a proteína derivada do gene encontra-se em fase experimental, isto é,
#ainda não está comprovado que de facto possa combater o organismo (Resultado: PA4425). A outra é um gene em que a proteína derivada não tem
#uma droga na base de dados DrugBank, confirmado pela não entrada "DrugBank" na base de dados da Pseudomonas (www.pseudomonas.com) para esse gene
#(Resultado: PA3145).

#Para cada proteína derivada do gene foram retiradas da internet informações relevantes, tais como, vias metabólicas onde se inserem, estrutura, motivos,
#domínios, função, ..., disponível no nosso website. Bases de dados utilizadas: KEGG, www.pseudomonas.com, UniProt, NCBI CDD, Pfam, PDB, LocTree3, NetPhosBac,
#Phobius e DrugBank.

######################################
#MultipleAlign e Árvore Filogenética
######################################

#função para escrever num ficheiro (para alinhamento múltiplo) as sequências resultantes de um BLAST
#tivemos que colocar só as sequências que alinharam porque se colocássemos a sequência completa que deu origem à que alinhou, dava erro a fazer
#o input do ficheiro com as sequências no clustalx
#::param gene,dicionario::gene que deve ser avaliado e dicionário que contém o gene e a respetiva sequência

def seqs_am(gene,dicionario):
  info = []
  seqs = []
  result = NCBIWWW.qblast("blastn","nr",str(dicionario[gene]),entrez_query = "NOT Pseudomonas[Organism]") #não queremos que apareça homologia com o organismo que estamos a estudar
  blast_result = NCBIXML.read(result)
  for alignment in blast_result.alignments:
    title = alignment.title.split("|")[3:5]
    f_title = title[0]+title[1]
    info.append(f_title)
    for hsp in alignment.hsps:
      seqs.append(hsp.sbjct)
   description = ">"+gene+"\n"
   seq = str(dicionario[gene])
   name_file = "sequences_"+gene+".fasta"
   file = open(name_file,"w")
   file.write(description)
   file.write(seq+"\n")
   for i in range(len(info)):
    file.write(">"+indo[i]+"(part of the sequence aligned)"+"\n")
    file.write(seqs[i]+"\n")
   file.close()
   return
   
#Chamar a função para cada gene que temos
seqs_am("PA4425",d_essenciais)
seqs_am("PA3145",d_essenciais)
seqs_am("PA4418",d_essenciais)

##Na linha de comandos chamar o "clustalx", executando este comando
##Fazer o input do ficheiro gerado pela função anterior, para cada gene
##Guardar o alinhamento em formato cluster e guardar a árvore em formato nexus

#Alinhamento é feito para cada ficheiro cluster

alignment = AlignIO.read(<nome_ficheiro_alinhamento_multiplo>,"clustal")

print(alignment) #com o print, retirar o número de colunas e de linhas do alinhamento
ncols = <numero_colunas>
nlinhas = <numero_linahs>

#Tentar encontrar um domínio/superfamília comum às sequências

#Função consensus estudada nas aulas de AASB, com a alteração para que seja feito num alinhamento múltiplo
# o consensus retornado pela função será o nosso hipotético motivo

def consensus (alig,nlinhas,ncols):
    cons = ""
    for i in range(ncols):
        cont = {}
        for k in range(nseqs):
            c = alig[k,i]
            if c in cont: cont[c] = cont[c] + 1
            else: cont[c] = 1
        maximum = 0
        cmax = None
        for ke in cont.keys():
            if ke != "-" and cont[ke] > maximum:
                maximum = cont[ke]
                cmax = ke
        cons = cons + cmax
    return cons

motif = consensus(alignment,nlinhas,ncols)
print(motif)
#Após obter o motivo basta copiar a sequência e colocar como query no NCBI CDD e verificar se ocorre um match
#ter em atenção que este é um método simples para tentar descobrir um motivo comum a todas as sequências
#estudos mais aprofundados podem e devem ser tidos em conta
 

#Árvores é feito para cada ficheiro nexus
tree = Phylo.read(<nome_ficheiro_arvore>,"nexus")
Phylo.draw_ascii(tree) 
   
    


 
