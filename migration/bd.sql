-- Migrations will appear here as you chat with AI

create table areas (
  id bigint primary key generated always as identity,
  nombre text not null
);

create table cargos (
  id bigint primary key generated always as identity,
  nombre text not null,
  area_id bigint not null references areas (id)
);

create table tipos_persona (
  id bigint primary key generated always as identity,
  tipo text not null,
  descripcion text not null,
  es_empleado boolean not null
);
/*
| id_tipo_persona | tipo | descripcion | es_empleado                                                                                                                        | es_empleado |
| 1  | Empleado    | Persona con vínculo laboral directo mediante contrato laboral con la empresa.                                                        | 1           |
| 2  | Visitante   | Persona externa sin vínculo contractual que ingresa de manera temporal por motivos específicos como auditoría, inspección o reunión. | 0           |
| 3  | Contratista | Persona natural o jurídica que presta servicios a la empresa mediante contrato de prestación de servicios.                           | 0           |
*/

create table personas (
  id bigint primary key generated always as identity,
  tipo_documento text not null,
  numero_documento text not null,
  nombres text not null,
  tipo_persona_id bigint not null references tipos_persona (id),
  cargo_id bigint references cargos (id)
);

create table registros (
  id bigint primary key generated always as identity,
  persona_id bigint not null references personas (id),
  evento text not null,
  vector_face vector
);

alter table areas
rename column id to id_area;

alter table cargos
rename column id to id_cargo;

alter table tipos_persona
rename column id to id_tipo_persona;

alter table personas
rename column id to id_persona;

alter table registros
rename column id to id_registro;