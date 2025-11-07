create database eduquiz;
use eduquiz;
-- USUÁRIOS
CREATE TABLE usuarios (
    id INT PRIMARY KEY AUTO_INCREMENT,
    nome VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    senha_hash VARCHAR(255) NOT NULL,
    tipo ENUM('aluno', 'professor') NOT NULL
);

-- CURSOS
CREATE TABLE cursos (
    id INT PRIMARY KEY AUTO_INCREMENT,
    nome VARCHAR(100) NOT NULL
);

-- ALUNOS
CREATE TABLE alunos (
    id INT PRIMARY KEY,
    curso_id INT NOT NULL,
    FOREIGN KEY (id) REFERENCES usuarios(id),
    FOREIGN KEY (curso_id) REFERENCES cursos(id)
);

-- PROFESSORES
CREATE TABLE professores (
    id INT PRIMARY KEY,
    FOREIGN KEY (id) REFERENCES usuarios(id)
);

-- ASSUNTOS
CREATE TABLE assuntos (
    id INT PRIMARY KEY AUTO_INCREMENT,
    nome VARCHAR(100) NOT NULL
);

-- NÍVEIS DE DIFICULDADE
CREATE TABLE niveis_dificuldade (
    id INT PRIMARY KEY AUTO_INCREMENT,
    descricao VARCHAR(50) NOT NULL
);

-- QUESTÕES
CREATE TABLE questoes (
    id INT PRIMARY KEY AUTO_INCREMENT,
    enunciado TEXT NOT NULL,
    nivel_id INT NOT NULL,
    assunto_id INT NOT NULL,
    autor_id INT NOT NULL,
    FOREIGN KEY (nivel_id) REFERENCES niveis_dificuldade(id),
    FOREIGN KEY (assunto_id) REFERENCES assuntos(id),
    FOREIGN KEY (autor_id) REFERENCES professores(id)
);

-- ALTERNATIVAS
CREATE TABLE alternativas (
    id INT PRIMARY KEY AUTO_INCREMENT,
    questao_id INT NOT NULL,
    texto TEXT NOT NULL,
    correta BOOLEAN NOT NULL,
    FOREIGN KEY (questao_id) REFERENCES questoes(id)
);

-- QUIZZES REALIZADOS
CREATE TABLE tentativas_quiz (
    id INT PRIMARY KEY AUTO_INCREMENT,
    aluno_id INT NOT NULL,
    nivel_id INT NOT NULL,
    FOREIGN KEY (aluno_id) REFERENCES alunos(id),
    FOREIGN KEY (nivel_id) REFERENCES niveis_dificuldade(id)
);

-- RESPOSTAS DOS ALUNOS
CREATE TABLE respostas_alunos (
    id INT PRIMARY KEY AUTO_INCREMENT,
    tentativa_id INT NOT NULL,
    questao_id INT NOT NULL,
    alternativa_id INT,
    correta BOOLEAN,
    FOREIGN KEY (tentativa_id) REFERENCES tentativas_quiz(id),
    FOREIGN KEY (questao_id) REFERENCES questoes(id),
    FOREIGN KEY (alternativa_id) REFERENCES alternativas(id)
);

-- MATERIAIS DE ESTUDO
CREATE TABLE materiais (
    id INT PRIMARY KEY AUTO_INCREMENT,
    professor_id INT NOT NULL,
    titulo VARCHAR(255) NOT NULL,
    url TEXT NOT NULL,
    FOREIGN KEY (professor_id) REFERENCES professores(id)
);

-- Primeiro remova a chave estrangeira antiga
ALTER TABLE materiais DROP FOREIGN KEY materiais_ibfk_1;

-- Agora adicione uma nova foreign key apontando para a tabela usuarios
ALTER TABLE materiais
  ADD CONSTRAINT fk_materiais_usuarios
  FOREIGN KEY (professor_id) REFERENCES usuarios(id);
  
  
ALTER TABLE materiais
ADD COLUMN descricao TEXT,
ADD COLUMN materia VARCHAR(100);

ALTER TABLE materiais ADD COLUMN data_publicacao DATETIME DEFAULT CURRENT_TIMESTAMP;

INSERT INTO niveis_dificuldade (descricao) VALUES ('Fácil'), ('Médio'), ('Difícil');
INSERT INTO assuntos (nome) VALUES ('Matemática'), ('História'), ('Química');

INSERT INTO usuarios (nome, email, senha_hash, tipo)
VALUES ('Administrador', 'adm@adm.com', SHA2('souadm', 256), 'adm');


ALTER TABLE usuarios
MODIFY COLUMN tipo ENUM('aluno', 'professor', 'adm') NOT NULL;


alter table cursos
modify column nome ENUM('Eletro', 'Info', 'Vestuário', 'Têxtil') NOT NULL;

INSERT INTO cursos (nome) VALUES 
('Eletro'),
('Info'),
('Vestuário'),
('Têxtil');




ALTER TABLE alunos DROP FOREIGN KEY alunos_ibfk_1;
ALTER TABLE alunos DROP FOREIGN KEY alunos_ibfk_2;

ALTER TABLE professores DROP FOREIGN KEY professores_ibfk_1;

ALTER TABLE questoes DROP FOREIGN KEY questoes_ibfk_1;
ALTER TABLE questoes DROP FOREIGN KEY questoes_ibfk_2;
ALTER TABLE questoes DROP FOREIGN KEY questoes_ibfk_3;

ALTER TABLE alternativas DROP FOREIGN KEY alternativas_ibfk_1;

ALTER TABLE tentativas_quiz DROP FOREIGN KEY tentativas_quiz_ibfk_1;
ALTER TABLE tentativas_quiz DROP FOREIGN KEY tentativas_quiz_ibfk_2;

ALTER TABLE respostas_alunos DROP FOREIGN KEY respostas_alunos_ibfk_1;
ALTER TABLE respostas_alunos DROP FOREIGN KEY respostas_alunos_ibfk_2;
ALTER TABLE respostas_alunos DROP FOREIGN KEY respostas_alunos_ibfk_3;

ALTER TABLE materiais DROP FOREIGN KEY fk_materiais_usuarios;
ALTER TABLE tentativas_quiz MODIFY COLUMN nivel_id INT NULL;



-- ALUNOS
ALTER TABLE alunos
ADD CONSTRAINT fk_alunos_usuarios
FOREIGN KEY (id) REFERENCES usuarios(id) ON DELETE CASCADE;

ALTER TABLE alunos
ADD CONSTRAINT fk_alunos_cursos
FOREIGN KEY (curso_id) REFERENCES cursos(id) ON DELETE CASCADE;

-- PROFESSORES
ALTER TABLE professores
ADD CONSTRAINT fk_professores_usuarios
FOREIGN KEY (id) REFERENCES usuarios(id) ON DELETE CASCADE;

-- QUESTOES
ALTER TABLE questoes
ADD CONSTRAINT fk_questoes_nivel
FOREIGN KEY (nivel_id) REFERENCES niveis_dificuldade(id) ON DELETE CASCADE;

ALTER TABLE questoes
ADD CONSTRAINT fk_questoes_assunto
FOREIGN KEY (assunto_id) REFERENCES assuntos(id) ON DELETE CASCADE;

ALTER TABLE questoes
ADD CONSTRAINT fk_questoes_professor
FOREIGN KEY (autor_id) REFERENCES professores(id) ON DELETE CASCADE;

-- ALTERNATIVAS
ALTER TABLE alternativas
ADD CONSTRAINT fk_alternativas_questao
FOREIGN KEY (questao_id) REFERENCES questoes(id) ON DELETE CASCADE;

-- TENTATIVAS DE QUIZ
ALTER TABLE tentativas_quiz
ADD CONSTRAINT fk_tentativa_aluno
FOREIGN KEY (aluno_id) REFERENCES alunos(id) ON DELETE CASCADE;

ALTER TABLE tentativas_quiz
ADD CONSTRAINT fk_tentativa_nivel
FOREIGN KEY (nivel_id) REFERENCES niveis_dificuldade(id) ON DELETE CASCADE;

-- RESPOSTAS DOS ALUNOS
ALTER TABLE respostas_alunos
ADD CONSTRAINT fk_resposta_tentativa
FOREIGN KEY (tentativa_id) REFERENCES tentativas_quiz(id) ON DELETE CASCADE;

ALTER TABLE respostas_alunos
ADD CONSTRAINT fk_resposta_questao
FOREIGN KEY (questao_id) REFERENCES questoes(id) ON DELETE CASCADE;

ALTER TABLE respostas_alunos
ADD CONSTRAINT fk_resposta_alternativa
FOREIGN KEY (alternativa_id) REFERENCES alternativas(id) ON DELETE SET NULL;

-- MATERIAIS
ALTER TABLE materiais
ADD CONSTRAINT fk_materiais_professor
FOREIGN KEY (professor_id) REFERENCES professores(id) ON DELETE CASCADE;

ALTER TABLE tentativas_quiz
ADD COLUMN data_hora DATETIME DEFAULT CURRENT_TIMESTAMP;

INSERT INTO assuntos (nome) VALUES 
('Números e Operações'),
('Geometria e Medidas'),
('Estatística e Probabilidade'),
('Álgebra e Funções'),
('Matemática Financeira e Aplicada');

delete from assuntos where id = 1;
delete from assuntos where id = 2;
delete from assuntos where id = 3;



ALTER TABLE tentativas_quiz ADD COLUMN assunto_id INT NULL AFTER nivel_id;
ALTER TABLE tentativas_quiz ADD CONSTRAINT fk_tentativa_assunto 
FOREIGN KEY (assunto_id) REFERENCES assuntos(id) ON DELETE SET NULL;

ALTER TABLE tentativas_quiz 
DROP FOREIGN KEY fk_tentativa_assunto;

ALTER TABLE tentativas_quiz 
ADD CONSTRAINT fk_tentativa_assunto 
FOREIGN KEY (assunto_id) REFERENCES assuntos(id) 
ON DELETE SET NULL ON UPDATE CASCADE;

-- Verifique se a coluna assunto_id permite NULL
SELECT IS_NULLABLE 
FROM INFORMATION_SCHEMA.COLUMNS 
WHERE TABLE_NAME = 'tentativas_quiz' AND COLUMN_NAME = 'assunto_id';

-- Verifique as constraints atuais
SELECT TABLE_NAME, COLUMN_NAME, CONSTRAINT_NAME, REFERENCED_TABLE_NAME, REFERENCED_COLUMN_NAME
FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
WHERE TABLE_NAME = 'tentativas_quiz' AND COLUMN_NAME = 'assunto_id';

SELECT * FROM alternativas;
select * from alunos;
select * from cursos;
SELECT * FROM niveis_dificuldade;
SELECT * FROM assuntos;
select * from usuarios;
select * from professores;
select * from tentativas_quiz;
select * from respostas_alunos;
select * from questoes;

ALTER TABLE tentativas_quiz ADD COLUMN tempo_gasto INT; -- segundos



-- ==========================
-- QUESTOES
-- ==========================

-- Certifique-se de ter ao menos 1 professor cadastrado:
-- (ajuste o id se necessário)
INSERT INTO usuarios (nome, email, senha_hash, tipo)
VALUES ('Prof.', 'prof@prof', SHA2('123', 256), 'professor');

INSERT INTO professores (id)
SELECT id FROM usuarios WHERE email = 'prof@prof';

SET @prof_id = (SELECT id FROM professores WHERE id = (SELECT id FROM usuarios WHERE email = 'prof@prof'));

-- ==========================
-- NÚMEROS E OPERAÇÕES
-- ==========================

-- Questão 1 (Fácil)
INSERT INTO questoes (enunciado, nivel_id, assunto_id, autor_id)
VALUES ('João comprou 3 pacotes de figurinhas. Cada pacote contém 8 figurinhas. Quantas figurinhas João tem ao todo?', 1, 4, @prof_id);
SET @q1 = LAST_INSERT_ID();
INSERT INTO alternativas (questao_id, texto, correta) VALUES
(@q1, '11', 0),
(@q1, '24', 1),
(@q1, '18', 0),
(@q1, '28', 0);

-- Questão 2 (Fácil)
INSERT INTO questoes (enunciado, nivel_id, assunto_id, autor_id)
VALUES ('Ana tinha R$ 50,00 e gastou R$ 18,00 em um lanche. Quanto sobrou para ela?', 1, 4, @prof_id);
SET @q2 = LAST_INSERT_ID();
INSERT INTO alternativas (questao_id, texto, correta) VALUES
(@q2, 'R$ 28,00', 1),
(@q2, 'R$ 30,00', 0),
(@q2, 'R$ 32,00', 0),
(@q2, 'R$ 36,00', 0);

-- Questão 3 (Fácil)
INSERT INTO questoes (enunciado, nivel_id, assunto_id, autor_id)
VALUES ('Um ônibus saiu de uma cidade com 40 passageiros. Em uma parada, desceram 12 pessoas e subiram 8. Quantas pessoas há no ônibus agora?', 1, 4, @prof_id);
SET @q3 = LAST_INSERT_ID();
INSERT INTO alternativas (questao_id, texto, correta) VALUES
(@q3, '36', 0),
(@q3, '38', 0),
(@q3, '40', 1),
(@q3, '42', 0);

-- Questão 4 (Médio)
INSERT INTO questoes (enunciado, nivel_id, assunto_id, autor_id)
VALUES ('Uma caixa tem 12 garrafas de suco. Cada garrafa contém 1,5 litro. Quantos litros há no total?', 2, 4, @prof_id);
SET @q4 = LAST_INSERT_ID();
INSERT INTO alternativas (questao_id, texto, correta) VALUES
(@q4, '15 L', 0),
(@q4, '16,5 L', 0),
(@q4, '17 L', 0),
(@q4, '18 L', 1);

-- Questão 5 (Médio)
INSERT INTO questoes (enunciado, nivel_id, assunto_id, autor_id)
VALUES ('Pedro tem 240 figurinhas. Ele quer dividir igualmente entre 8 amigos. Quantas figurinhas cada amigo vai receber?', 2, 4, @prof_id);
SET @q5 = LAST_INSERT_ID();
INSERT INTO alternativas (questao_id, texto, correta) VALUES
(@q5, '25', 0),
(@q5, '28', 0),
(@q5, '30', 1),
(@q5, '35', 0);

-- Questão 6 (Médio)
INSERT INTO questoes (enunciado, nivel_id, assunto_id, autor_id)
VALUES ('Uma padaria vendeu 3,5 kg de pão pela manhã e 4,25 kg à tarde. Quantos quilos de pão foram vendidos no total?', 2, 4, @prof_id);
SET @q6 = LAST_INSERT_ID();
INSERT INTO alternativas (questao_id, texto, correta) VALUES
(@q6, '7,25 kg', 1),
(@q6, '7,50 kg', 0),
(@q6, '8 kg', 0),
(@q6, '8,25 kg', 0);

-- Questão 7 (Difícil)
INSERT INTO questoes (enunciado, nivel_id, assunto_id, autor_id)
VALUES ('Um pedreiro usou 2,5 sacos de cimento por dia durante 6 dias. Quantos sacos ele usou ao todo?', 3, 4, @prof_id);
SET @q7 = LAST_INSERT_ID();
INSERT INTO alternativas (questao_id, texto, correta) VALUES
(@q7, '12,5 sacos', 1),
(@q7, '13 sacos', 0),
(@q7, '14 sacos', 0),
(@q7, '15 sacos', 0);

-- Questão 8 (Difícil)
INSERT INTO questoes (enunciado, nivel_id, assunto_id, autor_id)
VALUES ('Uma fábrica produz 120 peças por hora. Se trabalha 7,5 horas por dia, quantas peças são produzidas por dia?', 3, 4, @prof_id);
SET @q8 = LAST_INSERT_ID();
INSERT INTO alternativas (questao_id, texto, correta) VALUES
(@q8, '800', 0),
(@q8, '850', 0),
(@q8, '900', 1),
(@q8, '950', 0);

-- Questão 9 (Difícil)
INSERT INTO questoes (enunciado, nivel_id, assunto_id, autor_id)
VALUES ('Um tanque de 900 litros foi esvaziado igualmente em 6 horas. Quantos litros foram retirados por hora?', 3, 4, @prof_id);
SET @q9 = LAST_INSERT_ID();
INSERT INTO alternativas (questao_id, texto, correta) VALUES
(@q9, '120', 0),
(@q9, '130', 0),
(@q9, '140', 0),
(@q9, '150', 1);



-- ==========================
-- GEOMETRIA E MEDIDAS
-- ==========================

-- Questão 1 (Fácil)
INSERT INTO questoes (enunciado, nivel_id, assunto_id, autor_id)
VALUES ('Um retângulo tem base de 8 cm e altura de 5 cm. Qual é sua área?', 1, 5, @prof_id);
SET @q1 = LAST_INSERT_ID();
INSERT INTO alternativas (questao_id, texto, correta) VALUES
(@q1, '13 cm²', 0),
(@q1, '20 cm²', 0),
(@q1, '30 cm²', 1),
(@q1, '40 cm²', 0);

-- Questão 2 (Fácil)
INSERT INTO questoes (enunciado, nivel_id, assunto_id, autor_id)
VALUES ('Um triângulo tem base de 10 cm e altura de 6 cm. Qual é a sua área?', 1, 5, @prof_id);
SET @q2 = LAST_INSERT_ID();
INSERT INTO alternativas (questao_id, texto, correta) VALUES
(@q2, '15 cm²', 0),
(@q2, '25 cm²', 0),
(@q2, '30 cm²', 1),
(@q2, '60 cm²', 0);

-- Questão 3 (Fácil)
INSERT INTO questoes (enunciado, nivel_id, assunto_id, autor_id)
VALUES ('Um quadrado tem lado medindo 7 cm. Qual é o seu perímetro?', 1, 5, @prof_id);
SET @q3 = LAST_INSERT_ID();
INSERT INTO alternativas (questao_id, texto, correta) VALUES
(@q3, '14 cm', 0),
(@q3, '21 cm', 0),
(@q3, '28 cm', 1),
(@q3, '49 cm', 0);

-- Questão 4 (Médio)
INSERT INTO questoes (enunciado, nivel_id, assunto_id, autor_id)
VALUES ('Um terreno retangular mede 12 m de comprimento e 8 m de largura. Qual é a área total do terreno?', 2, 5, @prof_id);
SET @q4 = LAST_INSERT_ID();
INSERT INTO alternativas (questao_id, texto, correta) VALUES
(@q4, '80 m²', 0),
(@q4, '90 m²', 0),
(@q4, '96 m²', 1),
(@q4, '100 m²', 0);

-- Questão 5 (Médio)
INSERT INTO questoes (enunciado, nivel_id, assunto_id, autor_id)
VALUES ('Um círculo tem raio de 7 cm. Use π = 3,14. Qual é aproximadamente a área do círculo?', 2, 5, @prof_id);
SET @q5 = LAST_INSERT_ID();
INSERT INTO alternativas (questao_id, texto, correta) VALUES
(@q5, '120 cm²', 0),
(@q5, '145 cm²', 0),
(@q5, '150 cm²', 0),
(@q5, '153,86 cm²', 1);

-- Questão 6 (Médio)
INSERT INTO questoes (enunciado, nivel_id, assunto_id, autor_id)
VALUES ('Um cubo tem aresta de 3 cm. Qual é o seu volume?', 2, 5, @prof_id);
SET @q6 = LAST_INSERT_ID();
INSERT INTO alternativas (questao_id, texto, correta) VALUES
(@q6, '9 cm³', 0),
(@q6, '18 cm³', 0),
(@q6, '27 cm³', 1),
(@q6, '36 cm³', 0);

-- Questão 7 (Difícil)
INSERT INTO questoes (enunciado, nivel_id, assunto_id, autor_id)
VALUES ('Um retângulo tem perímetro de 50 cm. Se a base mede 15 cm, qual é a altura?', 3, 5, @prof_id);
SET @q7 = LAST_INSERT_ID();
INSERT INTO alternativas (questao_id, texto, correta) VALUES
(@q7, '10 cm', 1),
(@q7, '12 cm', 0),
(@q7, '15 cm', 0),
(@q7, '20 cm', 0);

-- Questão 8 (Difícil)
INSERT INTO questoes (enunciado, nivel_id, assunto_id, autor_id)
VALUES ('Um cilindro tem raio de 4 cm e altura de 10 cm. Use π = 3,14. Qual é o volume do cilindro?', 3, 5, @prof_id);
SET @q8 = LAST_INSERT_ID();
INSERT INTO alternativas (questao_id, texto, correta) VALUES
(@q8, '400 cm³', 0),
(@q8, '502,4 cm³', 1),
(@q8, '520 cm³', 0),
(@q8, '628 cm³', 0);

-- Questão 9 (Difícil)
INSERT INTO questoes (enunciado, nivel_id, assunto_id, autor_id)
VALUES ('Um triângulo isósceles tem dois lados medindo 10 cm e base de 12 cm. Qual é o perímetro desse triângulo?', 3, 5, @prof_id);
SET @q9 = LAST_INSERT_ID();
INSERT INTO alternativas (questao_id, texto, correta) VALUES
(@q9, '30 cm', 1),
(@q9, '32 cm', 0),
(@q9, '34 cm', 0),
(@q9, '36 cm', 0);



-- ==========================
-- ESTATÍSTICA E PROBABILIDADE
-- ==========================

-- Questão 1 (Fácil)
INSERT INTO questoes (enunciado, nivel_id, assunto_id, autor_id)
VALUES ('Uma pesquisa perguntou a 50 alunos qual era seu esporte favorito. 20 gostam de futebol, 15 de vôlei, 10 de basquete e 5 de natação. Quantos alunos não escolheram futebol?', 1, 6, @prof_id);
SET @q1 = LAST_INSERT_ID();
INSERT INTO alternativas (questao_id, texto, correta) VALUES
(@q1, '15', 0),
(@q1, '20', 0),
(@q1, '30', 1),
(@q1, '35', 0);

-- Questão 2 (Fácil)
INSERT INTO questoes (enunciado, nivel_id, assunto_id, autor_id)
VALUES ('Em uma caixa há 3 bolas vermelhas, 2 azuis e 5 verdes. Qual é o total de bolas?', 1, 6, @prof_id);
SET @q2 = LAST_INSERT_ID();
INSERT INTO alternativas (questao_id, texto, correta) VALUES
(@q2, '8', 0),
(@q2, '9', 0),
(@q2, '10', 1),
(@q2, '11', 0);

-- Questão 3 (Fácil)
INSERT INTO questoes (enunciado, nivel_id, assunto_id, autor_id)
VALUES ('Um dado comum tem 6 faces numeradas de 1 a 6. Qual é a probabilidade de sair um número par?', 1, 6, @prof_id);
SET @q3 = LAST_INSERT_ID();
INSERT INTO alternativas (questao_id, texto, correta) VALUES
(@q3, '1/3', 0),
(@q3, '1/2', 1),
(@q3, '2/3', 0),
(@q3, '5/6', 0);

-- Questão 4 (Médio)
INSERT INTO questoes (enunciado, nivel_id, assunto_id, autor_id)
VALUES ('A tabela mostra o número de livros lidos por 5 alunos em um mês: Ana=3, Bruno=5, Carla=2, Diego=4, Elisa=6. Qual é a média de livros lidos?', 2, 6, @prof_id);
SET @q4 = LAST_INSERT_ID();
INSERT INTO alternativas (questao_id, texto, correta) VALUES
(@q4, '3', 0),
(@q4, '4', 1),
(@q4, '5', 0),
(@q4, '6', 0);

-- Questão 5 (Médio)
INSERT INTO questoes (enunciado, nivel_id, assunto_id, autor_id)
VALUES ('Em uma turma, 40% dos alunos são meninos. Se a turma tem 30 alunos, quantas são meninas?', 2, 6, @prof_id);
SET @q5 = LAST_INSERT_ID();
INSERT INTO alternativas (questao_id, texto, correta) VALUES
(@q5, '10', 0),
(@q5, '12', 0),
(@q5, '18', 1),
(@q5, '20', 0);

-- Questão 6 (Médio)
INSERT INTO questoes (enunciado, nivel_id, assunto_id, autor_id)
VALUES ('Em uma pesquisa, 60% das pessoas preferem transporte público e o restante prefere carro particular. Se foram entrevistadas 200 pessoas, quantas preferem carro particular?', 2, 6, @prof_id);
SET @q6 = LAST_INSERT_ID();
INSERT INTO alternativas (questao_id, texto, correta) VALUES
(@q6, '60', 0),
(@q6, '70', 0),
(@q6, '80', 1),
(@q6, '100', 0);

-- Questão 7 (Difícil)
INSERT INTO questoes (enunciado, nivel_id, assunto_id, autor_id)
VALUES ('Em uma escola, 30% dos alunos praticam futebol, 25% vôlei, 15% basquete e o restante não pratica esportes. Qual a porcentagem dos que não praticam esportes?', 3, 6, @prof_id);
SET @q7 = LAST_INSERT_ID();
INSERT INTO alternativas (questao_id, texto, correta) VALUES
(@q7, '20%', 0),
(@q7, '25%', 0),
(@q7, '30%', 1),
(@q7, '35%', 0);

-- Questão 8 (Difícil)
INSERT INTO questoes (enunciado, nivel_id, assunto_id, autor_id)
VALUES ('Um baralho tem 52 cartas. Qual é a probabilidade de tirar uma carta de copas?', 3, 6, @prof_id);
SET @q8 = LAST_INSERT_ID();
INSERT INTO alternativas (questao_id, texto, correta) VALUES
(@q8, '1/2', 0),
(@q8, '1/4', 1),
(@q8, '1/3', 0),
(@q8, '1/13', 0);

-- Questão 9 (Difícil)
INSERT INTO questoes (enunciado, nivel_id, assunto_id, autor_id)
VALUES ('O gráfico mostra o número de visitantes em um parque durante a semana: Segunda=100, Terça=150, Quarta=200, Quinta=250, Sexta=300. Qual é o aumento percentual de segunda para sexta-feira?', 3, 6, @prof_id);
SET @q9 = LAST_INSERT_ID();
INSERT INTO alternativas (questao_id, texto, correta) VALUES
(@q9, '100%', 0),
(@q9, '150%', 1),
(@q9, '200%', 0),
(@q9, '250%', 0);



-- ==========================
-- ÁLGEBRA E FUNÇÕES
-- ==========================

-- Questão 1 (Fácil)
INSERT INTO questoes (enunciado, nivel_id, assunto_id, autor_id)
VALUES ('Resolva a equação: x + 5 = 9', 1, 7, @prof_id);
SET @q1 = LAST_INSERT_ID();
INSERT INTO alternativas (questao_id, texto, correta) VALUES
(@q1, '3', 0),
(@q1, '4', 1),
(@q1, '5', 0),
(@q1, '6', 0);

-- Questão 2 (Fácil)
INSERT INTO questoes (enunciado, nivel_id, assunto_id, autor_id)
VALUES ('Qual é o valor de y em y = 2x + 1 quando x = 3?', 1, 7, @prof_id);
SET @q2 = LAST_INSERT_ID();
INSERT INTO alternativas (questao_id, texto, correta) VALUES
(@q2, '5', 0),
(@q2, '6', 0),
(@q2, '7', 1),
(@q2, '8', 0);

-- Questão 3 (Fácil)
INSERT INTO questoes (enunciado, nivel_id, assunto_id, autor_id)
VALUES ('Simplifique a expressão: 3x + 2x', 1, 7, @prof_id);
SET @q3 = LAST_INSERT_ID();
INSERT INTO alternativas (questao_id, texto, correta) VALUES
(@q3, '5x', 1),
(@q3, '6x', 0),
(@q3, 'x^2', 0),
(@q3, '3x^2', 0);

-- Questão 4 (Médio)
INSERT INTO questoes (enunciado, nivel_id, assunto_id, autor_id)
VALUES ('Resolva: 2x - 4 = 10', 2, 7, @prof_id);
SET @q4 = LAST_INSERT_ID();
INSERT INTO alternativas (questao_id, texto, correta) VALUES
(@q4, '6', 1),
(@q4, '7', 0),
(@q4, '8', 0),
(@q4, '10', 0);

-- Questão 5 (Médio)
INSERT INTO questoes (enunciado, nivel_id, assunto_id, autor_id)
VALUES ('A função f(x) = 3x + 2. Qual é o valor de f(4)?', 2, 7, @prof_id);
SET @q5 = LAST_INSERT_ID();
INSERT INTO alternativas (questao_id, texto, correta) VALUES
(@q5, '10', 0),
(@q5, '12', 0),
(@q5, '14', 1),
(@q5, '16', 0);

-- Questão 6 (Médio)
INSERT INTO questoes (enunciado, nivel_id, assunto_id, autor_id)
VALUES ('Uma loja vende camisetas por R$ 30 cada. O total pago é dado por T = 30x, onde x é o número de camisetas. Quanto pagará alguém que comprar 5 camisetas?', 2, 7, @prof_id);
SET @q6 = LAST_INSERT_ID();
INSERT INTO alternativas (questao_id, texto, correta) VALUES
(@q6, 'R$ 100', 0),
(@q6, 'R$ 120', 0),
(@q6, 'R$ 150', 1),
(@q6, 'R$ 200', 0);

-- Questão 7 (Difícil)
INSERT INTO questoes (enunciado, nivel_id, assunto_id, autor_id)
VALUES ('Resolva a equação quadrática: x^2 - 5x + 6 = 0', 3, 7, @prof_id);
SET @q7 = LAST_INSERT_ID();
INSERT INTO alternativas (questao_id, texto, correta) VALUES
(@q7, 'x = 1 e x = 6', 0),
(@q7, 'x = 2 e x = 3', 1),
(@q7, 'x = 3 e x = 5', 0),
(@q7, 'x = 0 e x = 6', 0);

-- Questão 8 (Difícil)
INSERT INTO questoes (enunciado, nivel_id, assunto_id, autor_id)
VALUES ('Uma função é definida por f(x) = x^2 - 4x + 3. Qual é o valor mínimo dessa função?', 3, 7, @prof_id);
SET @q8 = LAST_INSERT_ID();
INSERT INTO alternativas (questao_id, texto, correta) VALUES
(@q8, '1', 1),
(@q8, '0', 0),
(@q8, '2', 0),
(@q8, '3', 0);

-- Questão 9 (Difícil)
INSERT INTO questoes (enunciado, nivel_id, assunto_id, autor_id)
VALUES ('O gráfico de uma função linear corta o eixo y em 2 e o eixo x em 4. Qual é a equação da função?', 3, 7, @prof_id);
SET @q9 = LAST_INSERT_ID();
INSERT INTO alternativas (questao_id, texto, correta) VALUES
(@q9, 'y = -1/2x + 2', 1),
(@q9, 'y = 2x + 4', 0),
(@q9, 'y = 1/2x - 2', 0),
(@q9, 'y = -x + 4', 0);



-- ==========================
-- MATEMÁTICA FINANCEIRA E APLICADA
-- ==========================

-- Questão 1 (Fácil)
INSERT INTO questoes (enunciado, nivel_id, assunto_id, autor_id)
VALUES ('Um produto custa R$ 100,00 e recebeu um desconto de 10%. Qual é o novo preço?', 1, 10, @prof_id);
SET @q1 = LAST_INSERT_ID();
INSERT INTO alternativas (questao_id, texto, correta) VALUES
(@q1, 'R$ 90,00', 1),
(@q1, 'R$ 95,00', 0),
(@q1, 'R$ 85,00', 0),
(@q1, 'R$ 80,00', 0);

-- Questão 2 (Fácil)
INSERT INTO questoes (enunciado, nivel_id, assunto_id, autor_id)
VALUES ('Se João ganha R$ 2.000,00 e recebe um aumento de 5%, quanto passa a ganhar?', 1, 10, @prof_id);
SET @q2 = LAST_INSERT_ID();
INSERT INTO alternativas (questao_id, texto, correta) VALUES
(@q2, 'R$ 2.050,00', 1),
(@q2, 'R$ 2.100,00', 0),
(@q2, 'R$ 2.200,00', 0),
(@q2, 'R$ 2.250,00', 0);

-- Questão 3 (Fácil)
INSERT INTO questoes (enunciado, nivel_id, assunto_id, autor_id)
VALUES ('Maria gastou R$ 45,00 de um total de R$ 90,00. Qual a porcentagem que ela gastou?', 1, 10, @prof_id);
SET @q3 = LAST_INSERT_ID();
INSERT INTO alternativas (questao_id, texto, correta) VALUES
(@q3, '25%', 0),
(@q3, '45%', 0),
(@q3, '50%', 1),
(@q3, '75%', 0);

-- Questão 4 (Médio)
INSERT INTO questoes (enunciado, nivel_id, assunto_id, autor_id)
VALUES ('Um celular custa R$ 1.200,00 à vista, mas pode ser parcelado em 6 vezes de R$ 220,00. Qual é o valor total pago a prazo e quanto de juros foi pago?', 2, 10, @prof_id);
SET @q4 = LAST_INSERT_ID();
INSERT INTO alternativas (questao_id, texto, correta) VALUES
(@q4, 'R$ 1.200,00 – R$ 0,00', 0),
(@q4, 'R$ 1.320,00 – R$ 120,00', 1),
(@q4, 'R$ 1.350,00 – R$ 150,00', 0),
(@q4, 'R$ 1.400,00 – R$ 200,00', 0);

-- Questão 5 (Médio)
INSERT INTO questoes (enunciado, nivel_id, assunto_id, autor_id)
VALUES ('Um capital de R$ 500,00 foi aplicado a 2% ao mês durante 4 meses em juros simples. Qual o valor dos juros?', 2, 10, @prof_id);
SET @q5 = LAST_INSERT_ID();
INSERT INTO alternativas (questao_id, texto, correta) VALUES
(@q5, 'R$ 30,00', 1),
(@q5, 'R$ 35,00', 0),
(@q5, 'R$ 40,00', 0),
(@q5, 'R$ 50,00', 0);

-- Questão 6 (Médio)
INSERT INTO questoes (enunciado, nivel_id, assunto_id, autor_id)
VALUES ('Um produto custava R$ 80,00 e sofreu aumento de 25%. Qual o novo preço?', 2, 10, @prof_id);
SET @q6 = LAST_INSERT_ID();
INSERT INTO alternativas (questao_id, texto, correta) VALUES
(@q6, 'R$ 85,00', 0),
(@q6, 'R$ 90,00', 0),
(@q6, 'R$ 95,00', 0),
(@q6, 'R$ 100,00', 1);

-- Questão 7 (Difícil)
INSERT INTO questoes (enunciado, nivel_id, assunto_id, autor_id)
VALUES ('Um investimento de R$ 2.000,00 rendeu 3% ao mês durante 6 meses em juros compostos. Qual o montante final?', 3, 10, @prof_id);
SET @q7 = LAST_INSERT_ID();
INSERT INTO alternativas (questao_id, texto, correta) VALUES
(@q7, 'R$ 2.200,00', 0),
(@q7, 'R$ 2.374,00', 1),
(@q7, 'R$ 2.500,00', 0),
(@q7, 'R$ 2.600,00', 0);

-- Questão 8 (Difícil)
INSERT INTO questoes (enunciado, nivel_id, assunto_id, autor_id)
VALUES ('Um empréstimo de R$ 1.500,00 foi feito a 4% ao mês em juros simples, por 8 meses. Qual será o montante total?', 3, 10, @prof_id);
SET @q8 = LAST_INSERT_ID();
INSERT INTO alternativas (questao_id, texto, correta) VALUES
(@q8, 'R$ 1.900,00', 1),
(@q8, 'R$ 1.920,00', 0),
(@q8, 'R$ 2.000,00', 0),
(@q8, 'R$ 2.100,00', 0);

-- Questão 9 (Difícil)
INSERT INTO questoes (enunciado, nivel_id, assunto_id, autor_id)
VALUES ('Uma loja oferece 10% de desconto à vista ou parcelamento em 3 vezes sem juros. Um cliente opta pelo parcelamento, mas o valor à vista é R$ 900,00. Qual o valor total que ele pagará parcelando?', 3, 10, @prof_id);
SET @q9 = LAST_INSERT_ID();
INSERT INTO alternativas (questao_id, texto, correta) VALUES
(@q9, 'R$ 900,00', 0),
(@q9, 'R$ 950,00', 0),
(@q9, 'R$ 1.000,00', 1),
(@q9, 'R$ 1.100,00', 0);



-- ==========================
-- Verificação final
-- ==========================
SELECT COUNT(*) AS total_questoes FROM questoes;
SELECT COUNT(*) AS total_alternativas FROM alternativas;



