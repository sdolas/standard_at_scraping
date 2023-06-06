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

# Wochentag extrahieren
wochentage <- c("Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag")
df <- df |> 
  mutate(weekday = factor(weekdays(pubdate, abbreviate = FALSE), levels = wochentage))

# PLOT
ggplot(df, aes(x = hms(pubtime), y = ..density.., 
               group = weekday, fill = weekday, color=weekday)) +
  geom_histogram(alpha = 1, bins=100) +
  scale_x_time(labels = scales::time_format("%H:00"),
               breaks = scales::pretty_breaks(n = 24),
               limits = c(hms("00:00:00"),
                          hms("23:59:59"))) +
  facet_wrap(~weekday, scales = "free_y", ncol = 1, labeller = label_parsed) +
  labs(title = "Verteilung der Veröffentlichungszeiten",
       x = "Uhrzeit",
       y = "Wochentag") +
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



# gefiltert nach top 10 autoren
# nach autor
top_authors <- df  |> 
  filter(!(origins %in% c("", "Redaktion"))) |> 
  count(origins, sort = TRUE) |> 
  head(10) |> 
  pull(origins)


df_filtered <- df |> 
  filter(origins %in% top_authors[10])

ggplot(df_filtered, aes(x = hms(pubtime), y = ..count.., 
                        group = weekday, fill = weekday, color=weekday)) +
  geom_histogram(alpha = 1, bins=100) +
  scale_x_time(labels = scales::time_format("%H:00"),
               breaks = scales::pretty_breaks(n = 24),
               limits = c(hms("00:00:00"),
                          hms("23:59:59"))) +
  facet_wrap(~weekday, scales = "fixed", ncol = 1, labeller = label_parsed) +
  labs(title = sprintf("Verteilung der Veröffentlichungszeiten für %s", df_filtered$origins[1]),
       x = "Uhrzeit",
       y = "Anzahl der Veröffentlichungen") +
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
