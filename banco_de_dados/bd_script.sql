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



USE eduquiz;

-- Certifique-se de ter ao menos 1 professor cadastrado:
-- (ajuste o id se necessário)

INSERT INTO usuarios (nome, email, senha_hash, tipo)
VALUES ('Prof.', 'prof@prof', SHA2('123', 256), 'professor');

INSERT INTO professores (id)
SELECT id FROM usuarios WHERE email = 'prof@prof';

SET @prof_id = (SELECT id FROM professores WHERE id = (SELECT id FROM usuarios WHERE email = 'prof@prof'));

-- Números e Operações

-- ===========================
-- QUESTÕES FÁCEIS (NÍVEL 1)
-- ===========================

-- Questão 1 (Fácil)
INSERT INTO questoes (enunciado, nivel_id, assunto_id, autor_id)
VALUES ('Maria tinha 15 balas e ganhou mais 12 de sua amiga. Quantas balas ela tem agora?', 1, @assunto_id, @prof_id);
SET @q1 = LAST_INSERT_ID();
INSERT INTO alternativas (questao_id, texto, correta) VALUES
(@q1, '25', 0),
(@q1, '26', 0),
(@q1, '27', 1),
(@q1, '28', 0);

-- Questão 2 (Fácil)
INSERT INTO questoes (enunciado, nivel_id, assunto_id, autor_id)
VALUES ('Carlos tinha R$ 20,00 e comprou um refrigerante de R$ 6,00. Quanto sobrou?', 1, @assunto_id, @prof_id);
SET @q2 = LAST_INSERT_ID();
INSERT INTO alternativas (questao_id, texto, correta) VALUES
(@q2, '12', 0),
(@q2, '13', 0),
(@q2, '14', 0),
(@q2, '14,00', 1);

-- Questão 3 (Fácil)
INSERT INTO questoes (enunciado, nivel_id, assunto_id, autor_id)
VALUES ('Um trem tem 8 vagões, e cada vagão tem 10 assentos. Quantos assentos há ao todo?', 1, @assunto_id, @prof_id);
SET @q3 = LAST_INSERT_ID();
INSERT INTO alternativas (questao_id, texto, correta) VALUES
(@q3, '60', 0),
(@q3, '70', 0),
(@q3, '80', 1),
(@q3, '90', 0);

-- Questão 4 (Fácil)
INSERT INTO questoes (enunciado, nivel_id, assunto_id, autor_id)
VALUES ('Em uma caixa há 36 bombons. Se forem divididos igualmente entre 6 pessoas, quantos bombons cada uma receberá?', 1, @assunto_id, @prof_id);
SET @q4 = LAST_INSERT_ID();
INSERT INTO alternativas (questao_id, texto, correta) VALUES
(@q4, '5', 0),
(@q4, '4', 0),
(@q4, '7', 0),
(@q4, '6', 1);

-- Questão 5 (Fácil)
INSERT INTO questoes (enunciado, nivel_id, assunto_id, autor_id)
VALUES ('O número 47 é composto por quantas dezenas e quantas unidades?', 1, @assunto_id, @prof_id);
SET @q5 = LAST_INSERT_ID();
INSERT INTO alternativas (questao_id, texto, correta) VALUES
(@q5, '4 dezenas e 7 unidades', 1),
(@q5, '3 dezenas e 17 unidades', 0),
(@q5, '5 dezenas e 2 unidades', 0),
(@q5, '7 dezenas e 4 unidades', 0);


-- ===========================
-- QUESTÕES MÉDIAS (NÍVEL 2)
-- ===========================

-- Questão 6 (Médio)
INSERT INTO questoes (enunciado, nivel_id, assunto_id, autor_id)
VALUES ('Uma padaria vendeu 85 pães de manhã e 67 à tarde. Quantos pães foram vendidos no total?', 2, @assunto_id, @prof_id);
SET @q6 = LAST_INSERT_ID();
INSERT INTO alternativas (questao_id, texto, correta) VALUES
(@q6, '142', 1),
(@q6, '145', 0),
(@q6, '150', 0),
(@q6, '152', 0);

-- Questão 7 (Médio)
INSERT INTO questoes (enunciado, nivel_id, assunto_id, autor_id)
VALUES ('Um caminhão transporta 125 caixas em cada viagem. Se ele fizer 8 viagens, quantas caixas transportará?', 2, @assunto_id, @prof_id);
SET @q7 = LAST_INSERT_ID();
INSERT INTO alternativas (questao_id, texto, correta) VALUES
(@q7, '900', 0),
(@q7, '950', 0),
(@q7, '1000', 1),
(@q7, '1050', 0);

-- Questão 8 (Médio)
INSERT INTO questoes (enunciado, nivel_id, assunto_id, autor_id)
VALUES ('Uma família gasta R$ 2.450,00 por mês. Quanto gastará em 5 meses?', 2, @assunto_id, @prof_id);
SET @q8 = LAST_INSERT_ID();
INSERT INTO alternativas (questao_id, texto, correta) VALUES
(@q8, 'R$ 10.250,00', 0),
(@q8, 'R$ 12.250,00', 0),
(@q8, 'R$ 12.450,00', 1),
(@q8, 'R$ 13.000,00', 0);

-- Questão 9 (Médio)
INSERT INTO questoes (enunciado, nivel_id, assunto_id, autor_id)
VALUES ('O triplo de um número é 48. Qual é esse número?', 2, @assunto_id, @prof_id);
SET @q9 = LAST_INSERT_ID();
INSERT INTO alternativas (questao_id, texto, correta) VALUES
(@q9, '12', 0),
(@q9, '14', 0),
(@q9, '15', 0),
(@q9, '16', 1);

-- Questão 10 (Médio)
INSERT INTO questoes (enunciado, nivel_id, assunto_id, autor_id)
VALUES ('Um terreno tem formato retangular com 25 m de comprimento e 18 m de largura. Qual é a área desse terreno?', 2, @assunto_id, @prof_id);
SET @q10 = LAST_INSERT_ID();
INSERT INTO alternativas (questao_id, texto, correta) VALUES
(@q10, '425 m²', 0),
(@q10, '440 m²', 0),
(@q10, '450 m²', 1),
(@q10, '475 m²', 0);


-- ===========================
-- QUESTÕES DIFÍCEIS (NÍVEL 3)
-- ===========================

-- Questão 11 (Difícil)
INSERT INTO questoes (enunciado, nivel_id, assunto_id, autor_id)
VALUES ('Uma máquina produz 320 peças por hora. Se funcionar 7 horas por dia, quantas peças são produzidas por dia?', 3, @assunto_id, @prof_id);
SET @q11 = LAST_INSERT_ID();
INSERT INTO alternativas (questao_id, texto, correta) VALUES
(@q11, '2.140', 0),
(@q11, '2.200', 1),
(@q11, '2.250', 0),
(@q11, '2.300', 0);

-- Questão 12 (Difícil)
INSERT INTO questoes (enunciado, nivel_id, assunto_id, autor_id)
VALUES ('Um tanque de 960 litros foi esvaziado em 8 horas de forma constante. Quantos litros saíram por hora?', 3, @assunto_id, @prof_id);
SET @q12 = LAST_INSERT_ID();
INSERT INTO alternativas (questao_id, texto, correta) VALUES
(@q12, '110', 0),
(@q12, '115', 0),
(@q12, '120', 1),
(@q12, '125', 0);

-- Questão 13 (Difícil)
INSERT INTO questoes (enunciado, nivel_id, assunto_id, autor_id)
VALUES ('Um número é o dobro de outro. Se a soma deles é 72, quais são esses números?', 3, @assunto_id, @prof_id);
SET @q13 = LAST_INSERT_ID();
INSERT INTO alternativas (questao_id, texto, correta) VALUES
(@q13, '24 e 48', 1),
(@q13, '26 e 46', 0),
(@q13, '30 e 42', 0),
(@q13, '20 e 52', 0);

-- Questão 14 (Difícil)
INSERT INTO questoes (enunciado, nivel_id, assunto_id, autor_id)
VALUES ('Em uma escola há 480 alunos. Se 3/8 deles são do turno da manhã, quantos estudam nesse turno?', 3, @assunto_id, @prof_id);
SET @q14 = LAST_INSERT_ID();
INSERT INTO alternativas (questao_id, texto, correta) VALUES
(@q14, '160', 0),
(@q14, '170', 0),
(@q14, '180', 1),
(@q14, '200', 0);

-- Questão 15 (Difícil)
INSERT INTO questoes (enunciado, nivel_id, assunto_id, autor_id)
VALUES ('Um caminhão percorreu 450 km com 50 litros de combustível. Quantos quilômetros percorre por litro?', 3, @assunto_id, @prof_id);
SET @q15 = LAST_INSERT_ID();
INSERT INTO alternativas (questao_id, texto, correta) VALUES
(@q15, '7', 0),
(@q15, '8', 0),
(@q15, '9', 1),
(@q15, '10', 0);

-- Geometria e Medidas

-- ===========================
-- QUESTÕES FÁCEIS (NÍVEL 1)
-- ===========================

-- Questão 1 (Fácil)
INSERT INTO questoes (enunciado, nivel_id, assunto_id, autor_id)
VALUES ('Um quadrado tem lados medindo 5 cm. Qual é o seu perímetro?', 1, @assunto_id, @prof_id);
SET @q1 = LAST_INSERT_ID();
INSERT INTO alternativas (questao_id, texto, correta) VALUES
(@q1, '10 cm', 0),
(@q1, '15 cm', 0),
(@q1, '20 cm', 1),
(@q1, '25 cm', 0);

-- Questão 2 (Fácil)
INSERT INTO questoes (enunciado, nivel_id, assunto_id, autor_id)
VALUES ('Qual é a forma geométrica que tem três lados?', 1, @assunto_id, @prof_id);
SET @q2 = LAST_INSERT_ID();
INSERT INTO alternativas (questao_id, texto, correta) VALUES
(@q2, 'Quadrado', 0),
(@q2, 'Triângulo', 1),
(@q2, 'Retângulo', 0),
(@q2, 'Círculo', 0);

-- Questão 3 (Fácil)
INSERT INTO questoes (enunciado, nivel_id, assunto_id, autor_id)
VALUES ('Um retângulo tem comprimento 8 cm e largura 4 cm. Qual é sua área?', 1, @assunto_id, @prof_id);
SET @q3 = LAST_INSERT_ID();
INSERT INTO alternativas (questao_id, texto, correta) VALUES
(@q3, '12 cm²', 0),
(@q3, '24 cm²', 1),
(@q3, '28 cm²', 0),
(@q3, '32 cm²', 0);

-- Questão 4 (Fácil)
INSERT INTO questoes (enunciado, nivel_id, assunto_id, autor_id)
VALUES ('Qual é o nome do sólido geométrico que tem 6 faces quadradas iguais?', 1, @assunto_id, @prof_id);
SET @q4 = LAST_INSERT_ID();
INSERT INTO alternativas (questao_id, texto, correta) VALUES
(@q4, 'Cubo', 1),
(@q4, 'Esfera', 0),
(@q4, 'Cilindro', 0),
(@q4, 'Cone', 0);

-- Questão 5 (Fácil)
INSERT INTO questoes (enunciado, nivel_id, assunto_id, autor_id)
VALUES ('Um círculo tem raio de 7 cm. Qual é o diâmetro?', 1, @assunto_id, @prof_id);
SET @q5 = LAST_INSERT_ID();
INSERT INTO alternativas (questao_id, texto, correta) VALUES
(@q5, '7 cm', 0),
(@q5, '10 cm', 0),
(@q5, '12 cm', 0),
(@q5, '14 cm', 1);


-- ===========================
-- QUESTÕES MÉDIAS (NÍVEL 2)
-- ===========================

-- Questão 6 (Médio)
INSERT INTO questoes (enunciado, nivel_id, assunto_id, autor_id)
VALUES ('Um triângulo tem base de 10 cm e altura de 6 cm. Qual é sua área?', 2, @assunto_id, @prof_id);
SET @q6 = LAST_INSERT_ID();
INSERT INTO alternativas (questao_id, texto, correta) VALUES
(@q6, '20 cm²', 0),
(@q6, '25 cm²', 0),
(@q6, '30 cm²', 1),
(@q6, '35 cm²', 0);

-- Questão 7 (Médio)
INSERT INTO questoes (enunciado, nivel_id, assunto_id, autor_id)
VALUES ('Qual é o volume de um cubo cujo lado mede 4 cm?', 2, @assunto_id, @prof_id);
SET @q7 = LAST_INSERT_ID();
INSERT INTO alternativas (questao_id, texto, correta) VALUES
(@q7, '16 cm³', 0),
(@q7, '32 cm³', 0),
(@q7, '48 cm³', 0),
(@q7, '64 cm³', 1);

-- Questão 8 (Médio)
INSERT INTO questoes (enunciado, nivel_id, assunto_id, autor_id)
VALUES ('Um terreno tem formato retangular e mede 12 m por 8 m. Qual é o seu perímetro?', 2, @assunto_id, @prof_id);
SET @q8 = LAST_INSERT_ID();
INSERT INTO alternativas (questao_id, texto, correta) VALUES
(@q8, '36 m', 0),
(@q8, '38 m', 0),
(@q8, '40 m', 1),
(@q8, '42 m', 0);

-- Questão 9 (Médio)
INSERT INTO questoes (enunciado, nivel_id, assunto_id, autor_id)
VALUES ('Um círculo tem raio de 3 cm. Use π = 3,14 e calcule sua área.', 2, @assunto_id, @prof_id);
SET @q9 = LAST_INSERT_ID();
INSERT INTO alternativas (questao_id, texto, correta) VALUES
(@q9, '18,84 cm²', 0),
(@q9, '28,26 cm²', 1),
(@q9, '30 cm²', 0),
(@q9, '32 cm²', 0);

-- Questão 10 (Médio)
INSERT INTO questoes (enunciado, nivel_id, assunto_id, autor_id)
VALUES ('Uma parede tem 2,5 m de altura e 4,2 m de largura. Qual é a área total?', 2, @assunto_id, @prof_id);
SET @q10 = LAST_INSERT_ID();
INSERT INTO alternativas (questao_id, texto, correta) VALUES
(@q10, '9,5 m²', 0),
(@q10, '10 m²', 0),
(@q10, '10,5 m²', 1),
(@q10, '11 m²', 0);


-- ===========================
-- QUESTÕES DIFÍCEIS (NÍVEL 3)
-- ===========================

-- Questão 11 (Difícil)
INSERT INTO questoes (enunciado, nivel_id, assunto_id, autor_id)
VALUES ('Um cilindro tem raio de 5 cm e altura de 10 cm. Use π = 3,14. Qual é o volume?', 3, @assunto_id, @prof_id);
SET @q11 = LAST_INSERT_ID();
INSERT INTO alternativas (questao_id, texto, correta) VALUES
(@q11, '785 cm³', 1),
(@q11, '800 cm³', 0),
(@q11, '820 cm³', 0),
(@q11, '900 cm³', 0);

-- Questão 12 (Difícil)
INSERT INTO questoes (enunciado, nivel_id, assunto_id, autor_id)
VALUES ('Um triângulo retângulo tem catetos de 9 cm e 12 cm. Qual é o comprimento da hipotenusa?', 3, @assunto_id, @prof_id);
SET @q12 = LAST_INSERT_ID();
INSERT INTO alternativas (questao_id, texto, correta) VALUES
(@q12, '14 cm', 0),
(@q12, '15 cm', 1),
(@q12, '16 cm', 0),
(@q12, '18 cm', 0);

-- Questão 13 (Difícil)
INSERT INTO questoes (enunciado, nivel_id, assunto_id, autor_id)
VALUES ('Uma piscina tem 6 m de comprimento, 4 m de largura e 1,5 m de profundidade. Qual é seu volume em litros?', 3, @assunto_id, @prof_id);
SET @q13 = LAST_INSERT_ID();
INSERT INTO alternativas (questao_id, texto, correta) VALUES
(@q13, '30.000 L', 0),
(@q13, '32.000 L', 1),
(@q13, '34.000 L', 0),
(@q13, '36.000 L', 0);

-- Questão 14 (Difícil)
INSERT INTO questoes (enunciado, nivel_id, assunto_id, autor_id)
VALUES ('Um terreno circular tem raio de 10 m. Use π = 3,14. Qual é o perímetro (circunferência)?', 3, @assunto_id, @prof_id);
SET @q14 = LAST_INSERT_ID();
INSERT INTO alternativas (questao_id, texto, correta) VALUES
(@q14, '31,4 m', 0),
(@q14, '62,8 m', 1),
(@q14, '65 m', 0),
(@q14, '70 m', 0);

-- Questão 15 (Difícil)
INSERT INTO questoes (enunciado, nivel_id, assunto_id, autor_id)
VALUES ('Um prisma retangular tem dimensões 5 cm, 8 cm e 10 cm. Qual é o volume?', 3, @assunto_id, @prof_id);
SET @q15 = LAST_INSERT_ID();
INSERT INTO alternativas (questao_id, texto, correta) VALUES
(@q15, '350 cm³', 0),
(@q15, '380 cm³', 0),
(@q15, '400 cm³', 1),
(@q15, '420 cm³', 0);

-- Estatística e Probabilidade

-- =========================
-- QUESTÕES FÁCEIS (NÍVEL 1)
-- =========================

-- Questão 1
INSERT INTO questoes (enunciado, nivel_id, assunto_id, autor_id)
VALUES ('Em uma pesquisa com 10 alunos, foram obtidas as seguintes idades: 13, 14, 13, 15, 14, 13, 16, 14, 13, 15. Qual é a moda das idades?', 1, @assunto_id, @prof_id);
SET @q1 = LAST_INSERT_ID();
INSERT INTO alternativas (questao_id, texto, correta) VALUES
(@q1, '13', 1),
(@q1, '14', 0),
(@q1, '15', 0),
(@q1, '16', 0);

-- Questão 2
INSERT INTO questoes (enunciado, nivel_id, assunto_id, autor_id)
VALUES ('Em uma urna há 4 bolas vermelhas e 6 bolas azuis. Qual é a probabilidade de retirar uma bola vermelha?', 1, @assunto_id, @prof_id);
SET @q2 = LAST_INSERT_ID();
INSERT INTO alternativas (questao_id, texto, correta) VALUES
(@q2, '40%', 1),
(@q2, '50%', 0),
(@q2, '60%', 0),
(@q2, '30%', 0);

-- Questão 3
INSERT INTO questoes (enunciado, nivel_id, assunto_id, autor_id)
VALUES ('As notas de Pedro foram: 6, 7, 8 e 9. Qual é a média aritmética?', 1, @assunto_id, @prof_id);
SET @q3 = LAST_INSERT_ID();
INSERT INTO alternativas (questao_id, texto, correta) VALUES
(@q3, '7,0', 0),
(@q3, '7,5', 1),
(@q3, '8,0', 0),
(@q3, '6,5', 0);

-- Questão 4
INSERT INTO questoes (enunciado, nivel_id, assunto_id, autor_id)
VALUES ('Um dado comum possui 6 faces numeradas de 1 a 6. Qual é a probabilidade de sair um número par?', 1, @assunto_id, @prof_id);
SET @q4 = LAST_INSERT_ID();
INSERT INTO alternativas (questao_id, texto, correta) VALUES
(@q4, '1/3', 0),
(@q4, '1/2', 1),
(@q4, '2/3', 0),
(@q4, '1/6', 0);

-- Questão 5
INSERT INTO questoes (enunciado, nivel_id, assunto_id, autor_id)
VALUES ('Em uma turma de 20 alunos, 8 são meninas. Qual é a porcentagem de meninas na turma?', 1, @assunto_id, @prof_id);
SET @q5 = LAST_INSERT_ID();
INSERT INTO alternativas (questao_id, texto, correta) VALUES
(@q5, '35%', 0),
(@q5, '40%', 1),
(@q5, '45%', 0),
(@q5, '50%', 0);

-- =========================
-- QUESTÕES MÉDIAS (NÍVEL 2)
-- =========================

-- Questão 6
INSERT INTO questoes (enunciado, nivel_id, assunto_id, autor_id)
VALUES ('Os salários de cinco funcionários são: 1200, 1300, 1300, 1400 e 2000. Qual é a mediana?', 2, @assunto_id, @prof_id);
SET @q6 = LAST_INSERT_ID();
INSERT INTO alternativas (questao_id, texto, correta) VALUES
(@q6, '1300', 1),
(@q6, '1400', 0),
(@q6, '1500', 0),
(@q6, '2000', 0);

-- Questão 7
INSERT INTO questoes (enunciado, nivel_id, assunto_id, autor_id)
VALUES ('Uma moeda é lançada 3 vezes. Qual é a probabilidade de sair cara em todas as jogadas?', 2, @assunto_id, @prof_id);
SET @q7 = LAST_INSERT_ID();
INSERT INTO alternativas (questao_id, texto, correta) VALUES
(@q7, '1/3', 0),
(@q7, '1/4', 0),
(@q7, '1/8', 1),
(@q7, '1/2', 0);

-- Questão 8
INSERT INTO questoes (enunciado, nivel_id, assunto_id, autor_id)
VALUES ('Em uma pesquisa, as idades dos participantes foram: 20, 22, 22, 23, 24, 25, 25, 25, 26, 30. Qual é a moda?', 2, @assunto_id, @prof_id);
SET @q8 = LAST_INSERT_ID();
INSERT INTO alternativas (questao_id, texto, correta) VALUES
(@q8, '22', 0),
(@q8, '25', 1),
(@q8, '23', 0),
(@q8, '26', 0);

-- Questão 9
INSERT INTO questoes (enunciado, nivel_id, assunto_id, autor_id)
VALUES ('Uma urna contém 5 bolas verdes, 3 vermelhas e 2 amarelas. Qual é a probabilidade de retirar uma bola vermelha?', 2, @assunto_id, @prof_id);
SET @q9 = LAST_INSERT_ID();
INSERT INTO alternativas (questao_id, texto, correta) VALUES
(@q9, '1/5', 0),
(@q9, '3/10', 1),
(@q9, '2/5', 0),
(@q9, '1/2', 0);

-- Questão 10
INSERT INTO questoes (enunciado, nivel_id, assunto_id, autor_id)
VALUES ('As temperaturas (em °C) registradas durante 5 dias foram: 22, 25, 24, 23, 26. Qual é a média?', 2, @assunto_id, @prof_id);
SET @q10 = LAST_INSERT_ID();
INSERT INTO alternativas (questao_id, texto, correta) VALUES
(@q10, '24', 1),
(@q10, '25', 0),
(@q10, '23', 0),
(@q10, '22', 0);

-- =========================
-- QUESTÕES DIFÍCEIS (NÍVEL 3)
-- =========================

-- Questão 11
INSERT INTO questoes (enunciado, nivel_id, assunto_id, autor_id)
VALUES ('Em uma fábrica, a probabilidade de uma peça ser defeituosa é de 5%. Qual é a probabilidade de uma amostra de 3 peças não ter nenhuma defeituosa?', 3, @assunto_id, @prof_id);
SET @q11 = LAST_INSERT_ID();
INSERT INTO alternativas (questao_id, texto, correta) VALUES
(@q11, '85,7%', 0),
(@q11, '90%', 0),
(@q11, '85%', 0),
(@q11, '85,7%', 1);

-- Questão 12
INSERT INTO questoes (enunciado, nivel_id, assunto_id, autor_id)
VALUES ('Os números 4, 6, 8 e 12 têm média 7,5. Qual seria a nova média se acrescentarmos o número 10?', 3, @assunto_id, @prof_id);
SET @q12 = LAST_INSERT_ID();
INSERT INTO alternativas (questao_id, texto, correta) VALUES
(@q12, '8', 1),
(@q12, '7,8', 0),
(@q12, '7,5', 0),
(@q12, '8,5', 0);

-- Questão 13
INSERT INTO questoes (enunciado, nivel_id, assunto_id, autor_id)
VALUES ('Um dado é lançado duas vezes. Qual é a probabilidade de sair um número par nas duas jogadas?', 3, @assunto_id, @prof_id);
SET @q13 = LAST_INSERT_ID();
INSERT INTO alternativas (questao_id, texto, correta) VALUES
(@q13, '1/2', 0),
(@q13, '1/3', 0),
(@q13, '1/4', 1),
(@q13, '2/3', 0);

-- Questão 14
INSERT INTO questoes (enunciado, nivel_id, assunto_id, autor_id)
VALUES ('A média de 8 números é 12. Se um número 16 for adicionado, qual será a nova média?', 3, @assunto_id, @prof_id);
SET @q14 = LAST_INSERT_ID();
INSERT INTO alternativas (questao_id, texto, correta) VALUES
(@q14, '12,5', 1),
(@q14, '13', 0),
(@q14, '11,5', 0),
(@q14, '12', 0);

-- Questão 15
INSERT INTO questoes (enunciado, nivel_id, assunto_id, autor_id)
VALUES ('Um concurso teve 500 participantes. 300 acertaram a primeira questão e 200 acertaram a segunda. Se 100 acertaram ambas, qual é a probabilidade de um participante escolhido ao acaso ter acertado pelo menos uma questão?', 3, @assunto_id, @prof_id);
SET @q15 = LAST_INSERT_ID();
INSERT INTO alternativas (questao_id, texto, correta) VALUES
(@q15, '80%', 1),
(@q15, '70%', 0),
(@q15, '60%', 0),
(@q15, '50%', 0);

-- Álgebra e Funções

-- ===========================
-- QUESTÕES FÁCEIS (NÍVEL 1)
-- ===========================

-- Questão 1
INSERT INTO questoes (enunciado, nivel_id, assunto_id, autor_id)
VALUES ('Resolva a equação: x + 5 = 12. Qual é o valor de x?', 1, @assunto_id, @prof_id);
SET @q1 = LAST_INSERT_ID();
INSERT INTO alternativas (questao_id, texto, correta) VALUES
(@q1, '5', 0),
(@q1, '6', 0),
(@q1, '7', 1),
(@q1, '8', 0);

-- Questão 2
INSERT INTO questoes (enunciado, nivel_id, assunto_id, autor_id)
VALUES ('Se y = 3x e x = 4, qual é o valor de y?', 1, @assunto_id, @prof_id);
SET @q2 = LAST_INSERT_ID();
INSERT INTO alternativas (questao_id, texto, correta) VALUES
(@q2, '7', 0),
(@q2, '10', 0),
(@q2, '12', 1),
(@q2, '14', 0);

-- Questão 3
INSERT INTO questoes (enunciado, nivel_id, assunto_id, autor_id)
VALUES ('A expressão 2a + 3a é igual a:', 1, @assunto_id, @prof_id);
SET @q3 = LAST_INSERT_ID();
INSERT INTO alternativas (questao_id, texto, correta) VALUES
(@q3, '5a', 1),
(@q3, '6a', 0),
(@q3, 'a²', 0),
(@q3, 'a + 6', 0);

-- Questão 4
INSERT INTO questoes (enunciado, nivel_id, assunto_id, autor_id)
VALUES ('Se uma função é dada por f(x) = x + 2, qual é o valor de f(5)?', 1, @assunto_id, @prof_id);
SET @q4 = LAST_INSERT_ID();
INSERT INTO alternativas (questao_id, texto, correta) VALUES
(@q4, '5', 0),
(@q4, '6', 0),
(@q4, '7', 1),
(@q4, '8', 0);

-- Questão 5
INSERT INTO questoes (enunciado, nivel_id, assunto_id, autor_id)
VALUES ('Simplifique a expressão: 4x + 3x', 1, @assunto_id, @prof_id);
SET @q5 = LAST_INSERT_ID();
INSERT INTO alternativas (questao_id, texto, correta) VALUES
(@q5, '6x', 0),
(@q5, '7x', 1),
(@q5, '8x', 0),
(@q5, '4x²', 0);

-- ===========================
-- QUESTÕES MÉDIAS (NÍVEL 2)
-- ===========================

-- Questão 6
INSERT INTO questoes (enunciado, nivel_id, assunto_id, autor_id)
VALUES ('Resolva a equação: 2x - 4 = 10. O valor de x é:', 2, @assunto_id, @prof_id);
SET @q6 = LAST_INSERT_ID();
INSERT INTO alternativas (questao_id, texto, correta) VALUES
(@q6, '5', 0),
(@q6, '6', 0),
(@q6, '7', 1),
(@q6, '8', 0);

-- Questão 7
INSERT INTO questoes (enunciado, nivel_id, assunto_id, autor_id)
VALUES ('A função f(x) = 2x + 1. Qual é o valor de f(4)?', 2, @assunto_id, @prof_id);
SET @q7 = LAST_INSERT_ID();
INSERT INTO alternativas (questao_id, texto, correta) VALUES
(@q7, '7', 0),
(@q7, '8', 0),
(@q7, '9', 1),
(@q7, '10', 0);

-- Questão 8
INSERT INTO questoes (enunciado, nivel_id, assunto_id, autor_id)
VALUES ('Qual é o valor de x na equação: 3x + 9 = 0?', 2, @assunto_id, @prof_id);
SET @q8 = LAST_INSERT_ID();
INSERT INTO alternativas (questao_id, texto, correta) VALUES
(@q8, '-3', 1),
(@q8, '0', 0),
(@q8, '3', 0),
(@q8, '9', 0);

-- Questão 9
INSERT INTO questoes (enunciado, nivel_id, assunto_id, autor_id)
VALUES ('Em uma função linear f(x) = 5x - 2, qual é o valor de f(3)?', 2, @assunto_id, @prof_id);
SET @q9 = LAST_INSERT_ID();
INSERT INTO alternativas (questao_id, texto, correta) VALUES
(@q9, '13', 1),
(@q9, '12', 0),
(@q9, '15', 0),
(@q9, '10', 0);

-- Questão 10
INSERT INTO questoes (enunciado, nivel_id, assunto_id, autor_id)
VALUES ('A expressão 2(x + 3) é equivalente a:', 2, @assunto_id, @prof_id);
SET @q10 = LAST_INSERT_ID();
INSERT INTO alternativas (questao_id, texto, correta) VALUES
(@q10, '2x + 6', 1),
(@q10, 'x + 6', 0),
(@q10, '2x + 3', 0),
(@q10, 'x² + 6', 0);

-- ===========================
-- QUESTÕES DIFÍCEIS (NÍVEL 3)
-- ===========================

-- Questão 11
INSERT INTO questoes (enunciado, nivel_id, assunto_id, autor_id)
VALUES ('Resolva a equação do 2º grau: x² - 5x + 6 = 0', 3, @assunto_id, @prof_id);
SET @q11 = LAST_INSERT_ID();
INSERT INTO alternativas (questao_id, texto, correta) VALUES
(@q11, 'x = 2 ou x = 3', 1),
(@q11, 'x = 1 ou x = 6', 0),
(@q11, 'x = 3 ou x = 5', 0),
(@q11, 'x = -2 ou x = -3', 0);

-- Questão 12
INSERT INTO questoes (enunciado, nivel_id, assunto_id, autor_id)
VALUES ('A função f(x) = x² - 4x + 3 tem raízes em:', 3, @assunto_id, @prof_id);
SET @q12 = LAST_INSERT_ID();
INSERT INTO alternativas (questao_id, texto, correta) VALUES
(@q12, 'x = 1 e x = 3', 1),
(@q12, 'x = 2 e x = 3', 0),
(@q12, 'x = 1 e x = 4', 0),
(@q12, 'x = 3 e x = 4', 0);

-- Questão 13
INSERT INTO questoes (enunciado, nivel_id, assunto_id, autor_id)
VALUES ('Qual é o vértice da parábola f(x) = x² - 6x + 8?', 3, @assunto_id, @prof_id);
SET @q13 = LAST_INSERT_ID();
INSERT INTO alternativas (questao_id, texto, correta) VALUES
(@q13, '(3, -1)', 1),
(@q13, '(2, -4)', 0),
(@q13, '(4, -2)', 0),
(@q13, '(3, 1)', 0);

-- Questão 14
INSERT INTO questoes (enunciado, nivel_id, assunto_id, autor_id)
VALUES ('Se f(x) = 2x² e g(x) = x + 1, qual é o valor de f(g(2))?', 3, @assunto_id, @prof_id);
SET @q14 = LAST_INSERT_ID();
INSERT INTO alternativas (questao_id, texto, correta) VALUES
(@q14, '18', 1),
(@q14, '12', 0),
(@q14, '10', 0),
(@q14, '8', 0);

-- Questão 15
INSERT INTO questoes (enunciado, nivel_id, assunto_id, autor_id)
VALUES ('Resolva: (x + 2)(x - 3) = 0', 3, @assunto_id, @prof_id);
SET @q15 = LAST_INSERT_ID();
INSERT INTO alternativas (questao_id, texto, correta) VALUES
(@q15, 'x = -2 ou x = 3', 1),
(@q15, 'x = 2 ou x = -3', 0),
(@q15, 'x = 3 ou x = 4', 0),
(@q15, 'x = -1 ou x = 3', 0);

-- Matemática Financeira e Aplicada

-- ============================================
-- Questões de Matemática Financeira e Aplicada
-- ============================================

SET @prof_id = 1;
SET @assunto_id = (SELECT id FROM assuntos WHERE nome = 'Matemática Financeira e Aplicada');

-- =========================
-- QUESTÕES FÁCEIS (NÍVEL 1)
-- =========================

-- Questão 1
INSERT INTO questoes (enunciado, nivel_id, assunto_id, autor_id)
VALUES ('Um produto custa R$ 200,00 e está com 10% de desconto. Qual é o valor do desconto?', 1, @assunto_id, @prof_id);
SET @q1 = LAST_INSERT_ID();
INSERT INTO alternativas (questao_id, texto, correta) VALUES
(@q1, 'R$ 15,00', 0),
(@q1, 'R$ 20,00', 1),
(@q1, 'R$ 25,00', 0),
(@q1, 'R$ 30,00', 0);

-- Questão 2
INSERT INTO questoes (enunciado, nivel_id, assunto_id, autor_id)
VALUES ('Maria comprou uma blusa de R$ 80,00 e pagou com uma nota de R$ 100,00. Quanto recebeu de troco?', 1, @assunto_id, @prof_id);
SET @q2 = LAST_INSERT_ID();
INSERT INTO alternativas (questao_id, texto, correta) VALUES
(@q2, 'R$ 15,00', 0),
(@q2, 'R$ 18,00', 0),
(@q2, 'R$ 20,00', 1),
(@q2, 'R$ 22,00', 0);

-- Questão 3
INSERT INTO questoes (enunciado, nivel_id, assunto_id, autor_id)
VALUES ('Um celular de R$ 1.000,00 teve aumento de 10%. Qual será o novo preço?', 1, @assunto_id, @prof_id);
SET @q3 = LAST_INSERT_ID();
INSERT INTO alternativas (questao_id, texto, correta) VALUES
(@q3, 'R$ 1.050,00', 0),
(@q3, 'R$ 1.080,00', 0),
(@q3, 'R$ 1.100,00', 1),
(@q3, 'R$ 1.120,00', 0);

-- Questão 4
INSERT INTO questoes (enunciado, nivel_id, assunto_id, autor_id)
VALUES ('Um produto custava R$ 250,00 e passou a custar R$ 200,00. Qual foi o percentual de desconto?', 1, @assunto_id, @prof_id);
SET @q4 = LAST_INSERT_ID();
INSERT INTO alternativas (questao_id, texto, correta) VALUES
(@q4, '15%', 0),
(@q4, '18%', 0),
(@q4, '20%', 1),
(@q4, '25%', 0);

-- Questão 5
INSERT INTO questoes (enunciado, nivel_id, assunto_id, autor_id)
VALUES ('Carlos aplicou R$ 1.000,00 e após 1 mês teve lucro de R$ 50,00. Qual foi o rendimento percentual?', 1, @assunto_id, @prof_id);
SET @q5 = LAST_INSERT_ID();
INSERT INTO alternativas (questao_id, texto, correta) VALUES
(@q5, '3%', 0),
(@q5, '4%', 0),
(@q5, '5%', 1),
(@q5, '6%', 0);

-- ==========================
-- QUESTÕES MÉDIAS (NÍVEL 2)
-- ==========================

-- Questão 6
INSERT INTO questoes (enunciado, nivel_id, assunto_id, autor_id)
VALUES ('Um capital de R$ 2.000,00 foi aplicado a juros simples de 2% ao mês durante 5 meses. Qual o montante final?', 2, @assunto_id, @prof_id);
SET @q6 = LAST_INSERT_ID();
INSERT INTO alternativas (questao_id, texto, correta) VALUES
(@q6, 'R$ 2.100,00', 0),
(@q6, 'R$ 2.150,00', 0),
(@q6, 'R$ 2.200,00', 1),
(@q6, 'R$ 2.250,00', 0);

-- Questão 7
INSERT INTO questoes (enunciado, nivel_id, assunto_id, autor_id)
VALUES ('Um empréstimo de R$ 1.200,00 foi feito a 3% ao mês, por 4 meses, com juros simples. Qual o valor total dos juros?', 2, @assunto_id, @prof_id);
SET @q7 = LAST_INSERT_ID();
INSERT INTO alternativas (questao_id, texto, correta) VALUES
(@q7, 'R$ 144,00', 1),
(@q7, 'R$ 120,00', 0),
(@q7, 'R$ 130,00', 0),
(@q7, 'R$ 150,00', 0);

-- Questão 8
INSERT INTO questoes (enunciado, nivel_id, assunto_id, autor_id)
VALUES ('Um produto teve aumento de 8% e passou a custar R$ 540,00. Qual era o preço anterior?', 2, @assunto_id, @prof_id);
SET @q8 = LAST_INSERT_ID();
INSERT INTO alternativas (questao_id, texto, correta) VALUES
(@q8, 'R$ 480,00', 0),
(@q8, 'R$ 490,00', 0),
(@q8, 'R$ 500,00', 1),
(@q8, 'R$ 510,00', 0);

-- Questão 9
INSERT INTO questoes (enunciado, nivel_id, assunto_id, autor_id)
VALUES ('Um investimento de R$ 5.000,00 rendeu R$ 600,00 após 6 meses. Qual foi a taxa de juros simples mensal?', 2, @assunto_id, @prof_id);
SET @q9 = LAST_INSERT_ID();
INSERT INTO alternativas (questao_id, texto, correta) VALUES
(@q9, '1,5%', 0),
(@q9, '2%', 0),
(@q9, '2,5%', 0),
(@q9, '2%', 1);

-- Questão 10
INSERT INTO questoes (enunciado, nivel_id, assunto_id, autor_id)
VALUES ('Um carro financiado por R$ 30.000,00 gera juros simples de 2% ao mês. Após 10 meses, quanto será pago de juros?', 2, @assunto_id, @prof_id);
SET @q10 = LAST_INSERT_ID();
INSERT INTO alternativas (questao_id, texto, correta) VALUES
(@q10, 'R$ 6.000,00', 1),
(@q10, 'R$ 5.000,00', 0),
(@q10, 'R$ 4.000,00', 0),
(@q10, 'R$ 7.000,00', 0);

-- ===========================
-- QUESTÕES DIFÍCEIS (NÍVEL 3)
-- ===========================

-- Questão 11
INSERT INTO questoes (enunciado, nivel_id, assunto_id, autor_id)
VALUES ('Um capital de R$ 1.000,00 foi aplicado a juros compostos de 5% ao mês por 3 meses. Qual será o montante final?', 3, @assunto_id, @prof_id);
SET @q11 = LAST_INSERT_ID();
INSERT INTO alternativas (questao_id, texto, correta) VALUES
(@q11, 'R$ 1.150,00', 0),
(@q11, 'R$ 1.157,63', 1),
(@q11, 'R$ 1.160,00', 0),
(@q11, 'R$ 1.200,00', 0);

-- Questão 12
INSERT INTO questoes (enunciado, nivel_id, assunto_id, autor_id)
VALUES ('Um valor de R$ 2.000,00 foi aplicado a juros compostos de 3% ao mês por 6 meses. Qual o montante?', 3, @assunto_id, @prof_id);
SET @q12 = LAST_INSERT_ID();
INSERT INTO alternativas (questao_id, texto, correta) VALUES
(@q12, 'R$ 2.360,00', 0),
(@q12, 'R$ 2.380,00', 0),
(@q12, 'R$ 2.382,03', 1),
(@q12, 'R$ 2.400,00', 0);

-- Questão 13
INSERT INTO questoes (enunciado, nivel_id, assunto_id, autor_id)
VALUES ('Um investimento dobrou em 10 meses sob juros compostos de 7,18% ao mês. Isso confirma a "regra dos 70"?', 3, @assunto_id, @prof_id);
SET @q13 = LAST_INSERT_ID();
INSERT INTO alternativas (questao_id, texto, correta) VALUES
(@q13, 'Sim, aproximadamente', 1),
(@q13, 'Não, o tempo seria maior', 0),
(@q13, 'Não, o tempo seria menor', 0),
(@q13, 'Depende da taxa efetiva', 0);

-- Questão 14
INSERT INTO questoes (enunciado, nivel_id, assunto_id, autor_id)
VALUES ('Uma dívida de R$ 5.000,00 será quitada em 12 meses com juros compostos de 2% ao mês. Qual será o valor final aproximado?', 3, @assunto_id, @prof_id);
SET @q14 = LAST_INSERT_ID();
INSERT INTO alternativas (questao_id, texto, correta) VALUES
(@q14, 'R$ 6.000,00', 0),
(@q14, 'R$ 6.200,00', 0),
(@q14, 'R$ 6.340,00', 1),
(@q14, 'R$ 6.500,00', 0);

-- Questão 15
INSERT INTO questoes (enunciado, nivel_id, assunto_id, autor_id)
VALUES ('Um investimento de R$ 3.000,00 rende 4% ao mês. Após 1 ano, qual será o montante total em juros compostos?', 3, @assunto_id, @prof_id);
SET @q15 = LAST_INSERT_ID();
INSERT INTO alternativas (questao_id, texto, correta) VALUES
(@q15, 'R$ 4.500,00', 0),
(@q15, 'R$ 4.734,00', 1),
(@q15, 'R$ 4.800,00', 0),
(@q15, 'R$ 5.000,00', 0);






