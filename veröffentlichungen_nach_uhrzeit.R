librarian::shelf("RSQLite", "ggplot2", "tidyr", "purrr", "ggnewscale", 
                 "dplyr", "lubridate", "tidytext", "stringr")

Sys.setlocale(category = "LC_TIME", locale = "German")
setwd("C:\\Users\\user00\\Documents\\GitHub\\standard_at_scraping")
load("sentiws.RData")

# lade Daten
db <- "C:\\Users\\user00\\Documents\\GitHub\\standard_at_scraping\\article_data.db" # speichere pfad zur Datenbank
con <- dbConnect(drv=RSQLite::SQLite(), dbname=db) # Verbinde mit der Datenbank
tables <- dbListTables(con) # speichere alle Tabellen der Datenbank
tables <- tables[tables != "sqlite_sequence"] # entferne sqlite_sequence (beinhaltet tabelleninformation)
data <- dbGetQuery(conn=con, statement=paste0("SELECT * FROM '", tables[[1]], "'"))
data$pubdate <- strptime(data$pubdate, format = "%Y-%m-%d %H:%M:%S")
df <- data

# erstelle Spalte mit lediglich Uhrzeiten
df$pubtime <- format(as.POSIXct(df$pubdate, tz = "CET"), "%H:%M:%S")

# nach kicker
top_kickers <- df  |> 
  count(kicker, sort = TRUE) |> 
  head(10) |> 
  pull(kicker)

df_filtered <- df |> 
  filter(kicker %in% top_kickers)

# PLOT
ggplot(df_filtered, aes(x = hms(pubtime), y = ..density.., group = kicker, fill = kicker, color=kicker)) +
  geom_density(alpha = 1) +
  scale_x_time(labels = scales::time_format("%H:00"),
               breaks = scales::pretty_breaks(n = 24),
               limits = c(hms("00:00:00"),
                          hms("23:59:59"))) +
  facet_wrap(~kicker, scales = "free_y", ncol = 1, labeller = label_parsed) +
  labs(title = "Verteilung der Veröffentlichungszeiten nach Rubrik",
       x = "Uhrzeit",
       y = "Dichte der Veröffentlichungen") +
  theme_minimal() +
  theme(legend.title = element_text("Kicker", face = "bold"),
        legend.position = "none",
        strip.background = element_blank(),
        axis.ticks.y = element_blank(),
        axis.text.y = element_blank(),
        panel.grid.major = element_blank(),
        panel.grid.minor = element_blank(),
        plot.background = element_rect(fill = "white", colour = NA),
        panel.background = element_rect(fill = "white", colour = NA))



# nach autor
top_authors <- df  |> 
  filter(!(origins %in% c("", "Redaktion"))) |> 
  count(origins, sort = TRUE) |> 
  head(10) |> 
  pull(origins)

df_filtered <- df |> 
  filter(origins %in% top_authors)

# PLOT
ggplot(df_filtered, aes(x = hms(pubtime), y = ..density.., group = origins, fill = origins, color=origins)) +
  geom_histogram(alpha = 1, bins=100) +
  scale_x_time(labels = scales::time_format("%H:00"),
               breaks = scales::pretty_breaks(n = 24),
               limits = c(hms("00:00:00"),
                          hms("23:59:59"))) +
  facet_wrap(~origins, scales = "free_y", ncol = 1) +
  labs(title = "Wer veröffentlicht wann?",
       x = "Uhrzeit",
       y = "Dichte der Veröffentlichungen") +
  theme_minimal() +
  theme(legend.title = element_text("Kicker", face = "bold"),
        legend.position = "none",
        strip.background = element_blank(),
        axis.ticks.y = element_blank(),
        axis.text.y = element_blank(),
        panel.grid.major = element_blank(),
        panel.grid.minor = element_blank(),
        plot.background = element_rect(fill = "white", colour = NA),
        panel.background = element_rect(fill = "white", colour = NA))