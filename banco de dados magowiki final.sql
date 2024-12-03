create database magowiki;
use magowiki;

create table usuarios(
id_usuario int primary key auto_increment,
email varchar(500) not null,
nome varchar(500) not null,
senha varchar(500) not null,
PFP varchar(3000),
usuario_tipo varchar(45)

);

select * from usuarios;

SELECT SENHA, EMAIL, NOME, PFP, USUARIO_TIPO, ID_USUARIO FROM USUARIOS WHERE EMAIL = "a1@a1";

insert into usuarios(email, nome, senha, PFP)
values("a@a", "teste", "123", "https://i.pinimg.com/564x/30/e1/5e/30e15eac3bc417e6668dd16ccb01107b.jpg");
select * from usuarios;

create table magias(
id_magia int primary key auto_increment,
nome_magia varchar(500) not null,
id_sistema int,
alcance varchar(300) not null,
id_classe int,
nivel_uso int not null,
imagem varchar(3000),
descricao varchar(3000),
duracao varchar(600),
id_usuario int,
tempo_conjuracao varchar(100),

foreign key (id_classe) references classes (id_classe) on delete set null,
foreign key (id_sistema) references sistemas (id_sistema) on delete set null,
foreign key (id_usuario) references usuarios (id_usuario) on delete set null
);

drop table magias;

insert into magias(nome_magia, id_sistema, alcance, id_classe, nivel_uso, imagem, descricao, id_usuario)
values("andar na água", 1, "9", 3, 3, "https://i.pinimg.com/564x/46/6d/90/466d906a4ddd8c0c33d0584f4ccef9c2.jpg", "Deixa andar em superficies liquidas", 2);

select m.*, s.nome_sistema, c.nome_classe, u.nome
from magias m inner join sistemas s on m.id_sistema = s.id_sistema
			  inner join classes c on m.id_classe = c.id_classe
			  inner join usuarios u on m.id_usuario = u.id_usuario;

create table classes(
id_classe int primary key auto_increment,
nome_classe varchar(400),
descricao_classe varchar(400),
id_usuario int,

foreign key (id_usuario) references usuarios (id_usuario) on delete set null
);

drop table classes;

insert into classes(nome_classe, id_usuario)
values("Bruxo", 2);

create table sistemas(
id_sistema int primary key auto_increment,
nome_sistema varchar(400),
id_usuario int,

foreign key (id_usuario) references usuarios (id_usuario) on delete set null
);

drop table sistemas;
insert into sistemas(nome_sistema, id_usuario)
values("sistema pra excluir", 2);

SELECT * FROM sistemas;

drop table sistemas;

select m.*, s.nome_sistema, c.nome_classe, u.nome
from magias m inner join sistemas s on m.id_sistema = s.id_sistema
			  inner join classes c on m.id_classe = c.id_classe
			  inner join usuarios u on m.id_usuario = u.id_usuario order by id_magia;


select m.*, s.nome_sistema
from magias m inner join sistemas s on m.id_sistema = s.id_sistema
where nome_sistema like "%D%";

select * from magias where nome_magia like "%acal%";

select m.*, c.nome_classe
from magias m inner join classes c on m.id_classe = c.id_classe
where nome_classe like "%bar%";

select * from sistemas where id_usuario = 2;

select * from classes;

SELECT COUNT(*) AS total_magias FROM MAGIAS WHERE ID_USUARIO = 2;

create table favoritos(
id_favorito int auto_increment primary key,

id_usuario int,
id_magia int,

foreign key (id_usuario) references usuarios (id_usuario) on delete set null,
foreign key (id_magia) references magias (id_magia) on delete set null
);

insert into favoritos (id_usuario, id_magia)
value(3, 4);

select * from usuarios;
select * from magias;

select * from favoritos;

select f.*, u.nome, m.*
from favoritos f inner join usuarios u on f.id_usuario = u.id_usuario
				 inner join magias m on f.id_magia = m.id_magia
                 where u.id_usuario = 3;
                 

select m.*, s.nome_sistema, c.nome_classe, u.nome
from magias m inner join sistemas s on m.id_sistema = s.id_sistema
			  inner join classes c on m.id_classe = c.id_classe
			  inner join usuarios u on m.id_usuario = u.id_usuario order by id_magia;

SELECT f.*, m.*, s.nome_sistema, c.nome_classe
        FROM favoritos f
        INNER JOIN magias m ON f.id_magia = m.id_magia
        INNER JOIN sistemas s ON m.id_sistema = s.id_sistema
        INNER JOIN classes c ON m.id_classe = c.id_classe
        WHERE f.id_usuario = 3;
        
        
        








