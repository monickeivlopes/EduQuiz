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

ALTER TABLE materiais DROP FOREIGN KEY materiais_ibfk_1;

-- Agora adicione uma nova foreign key apontando para a tabela usuarios
ALTER TABLE materiais
  ADD CONSTRAINT fk_materiais_usuarios
  FOREIGN KEY (professor_id) REFERENCES usuarios(id);

ALTER TABLE materiais
  ADD COLUMN descricao TEXT,
  ADD COLUMN materia VARCHAR(100);
