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


INSERT INTO niveis_dificuldade (descricao)
VALUES ('Fácil'), ('Médio'), ('Difícil');

INSERT INTO usuarios (nome, email, senha_hash, tipo)
VALUES ('Administrador', 'adm@gmail.com', SHA2('souadm@eduquiz', 256), 'adm');

INSERT INTO usuarios (nome, email, senha_hash, tipo)
VALUES ('Administrador', 'adm@adm', SHA2('123', 256), 'adm');

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