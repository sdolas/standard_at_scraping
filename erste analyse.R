librarian::shelf("RSQLite", "ggplot2", "tidyr", "purrr", "dplyr", "lubridate")

# speichere pfad zur Datenbank
db <- "C:\\Users\\user00\\Documents\\GitHub\\standard_at_scraping\\article_data.db"

## Verbinde mit der Datenbank
con <- dbConnect(drv=RSQLite::SQLite(), dbname=db)

## speichere alle Tabellen der Datenbank
tables <- dbListTables(con)

## entferne sqlite_sequence (beinhaltet tabelleninformation)
tables <- tables[tables != "sqlite_sequence"]

# lade daten
data <- dbGetQuery(conn=con, statement=paste0("SELECT * FROM '", tables[[1]], "'"))
data$pubdate <- as.Date(data$pubdate)

df <- data

# erhalte die 5 größten kicker
tmp <- data |> group_by(kicker) |> summarise(n = n())
topkicker <- tmp[order(tmp$n, decreasing = T),] |> head(10)

df$new_kicker <- ifelse(df$kicker %in% topkicker$kicker, df$kicker, "sonstiges")

# erstelle tageslabel:
df$day <- as.Date(cut(df$pubdate, breaks="day"), format="%Y-%m-%d")

# erstelle wochenlabel:
df$week <- as.Date(cut(df$pubdate, breaks="week"), format="%Y-%m-%d")

df_1 <- df |> filter(new_kicker!="sonstiges") |>  group_by(week, new_kicker) |>
  summarise(n = sum(n())) |>
  mutate(percentage = n / sum(n))

g <- ggplot(df_1, aes(x=week, y=percentage,group=new_kicker, fill=new_kicker))
g + geom_area() + 
  scale_x_date(date_breaks = "3 month", date_labels = "%b-%Y")


g <- ggplot(df_1, aes(x=week, y=n, group=new_kicker, fill=new_kicker,colour=new_kicker))
g + geom_line() + 
  scale_x_date(date_breaks = "3 month", date_labels = "%b-%Y")

##########
tmp <- data |> group_by(origins) |> summarise(n = n())
toporigins <- tmp[order(tmp$n, decreasing = T),] |> head(50)
toporigins <- toporigins[!(toporigins$origins %in% c("","Redaktion","APA", "AP", "APA, dpa", "Reuters", "dpa")),]

df_2 <- df[(df$origins %in% toporigins$origins) & year(df$pubdate)>=2002,] |> group_by(day, origins) |> 
  summarise(n=n())

g <- ggplot(df_2, aes(x=day, y=origins))
g + geom_tile()
