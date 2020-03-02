/* Thanks to Alexey https://github.com/alexey-goloburdin/telegram-finance-bot/blob/master/createdb.sql */

create table budget(
    codename    text primary key,
    daily_limit integer
);

create table category(
    codename        text primary key,
    name            text,
    is_base_expense integer,
    aliases         text
);

create table expense(
    id                integer primary key,
    amount            integer,
    created           text,
    category_codename integer,
    raw_text          text,
    foreign key(category_codename) references category(codename)
);

insert into category (codename, name, is_base_expense, aliases)
values
    ("products", "продукты", true, "еда"),
    ("coffee", "кофе", true, ""),
    ("dinner", "обед", true, "столовая, ланч, бизнес-ланч, бизнес ланч"),
    ("cafe", "кафе", true, "ресторан, рест, мак, макдональдс, макдак, kfc, ilpatio, il patio"),
    ("transport", "общ. транспорт", false, "метро, автобус, metro"),
    ("taxi", "такси", false, "яндекс такси, yandex taxi"),
    ("phone", "телефон", false, "теле2, связь"),
    ("books", "книги", false, "литература, литра, лит-ра"),
    ("study", "учеба", true, "курсы, инглиш, курс"),
    ("internet", "интернет", false, "инет, inet"),
    ("subscriptions", "подписки", false, "подписка"),
    ("other", "прочее", true, "");

insert into budget(codename, daily_limit) values ('base', 500);