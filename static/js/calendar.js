document.addEventListener("DOMContentLoaded", function () {

    const calendarEl = document.getElementById("calendar");

    const calendar = new FullCalendar.Calendar(calendarEl, {

        initialView: "dayGridMonth",

        locale: "fr",

        height: "auto",

        headerToolbar: {
            left: "prev,next today",
            center: "title",
            right: "dayGridMonth,timeGridWeek,listWeek"
        },

        buttonText: {
            today: "Aujourd'hui",
            month: "Mois",
            week: "Semaine",
            list: "Liste"
        },

        // =====================================================
        // RÉCUPÉRATION DES ÉVÉNEMENTS
        // =====================================================

        events: async function (fetchInfo, successCallback, failureCallback) {

            try {

                const response = await fetch("/api/events");

                if (!response.ok) {
                    throw new Error(
                        `Erreur HTTP : ${response.status}`
                    );
                }

                const data = await response.json();

                const events = data.map(event => ({

                    id: event.id,

                    title: event.name,

                    start: event.start_time,

                    end: event.end_time,

                    extendedProps: {
                        description: event.description || "",
                        image_url: event.image_url || "",
                        location: event.location || "",
                        status: event.status || "",
                        event_url: event.event_url || ""
                    }

                }));

                successCallback(events);

            } catch (error) {

                console.error(
                    "Erreur lors du chargement des événements :",
                    error
                );

                failureCallback(error);
            }
        },

        // =====================================================
        // RENDU PERSONNALISÉ DES ÉVÉNEMENTS
        // =====================================================

        eventContent: function (arg) {

            const event = arg.event;

            const imageUrl =
                event.extendedProps.image_url;

            const title =
                event.title || "Événement";

            // Création de la carte
            const card = document.createElement("div");

            card.classList.add("event-card");

            // -------------------------------------------------
            // IMAGE
            // -------------------------------------------------

            if (imageUrl) {

                card.style.backgroundImage =
                    `url("${imageUrl}")`;

            } else {

                card.classList.add("no-image");
            }

            // -------------------------------------------------
            // CONTENU
            // -------------------------------------------------

            const content =
                document.createElement("div");

            content.classList.add("event-content");

            // Titre
            const titleElement =
                document.createElement("div");

            titleElement.classList.add("event-title");

            titleElement.textContent = title;

            content.appendChild(titleElement);

            // Heure
            if (event.start) {

                const timeElement =
                    document.createElement("div");

                timeElement.classList.add("event-time");

                const startTime =
                    event.start.toLocaleTimeString(
                        "fr-FR",
                        {
                            hour: "2-digit",
                            minute: "2-digit"
                        }
                    );

                let timeText = startTime;

                if (event.end) {

                    const endTime =
                        event.end.toLocaleTimeString(
                            "fr-FR",
                            {
                                hour: "2-digit",
                                minute: "2-digit"
                            }
                        );

                    timeText =
                        `${startTime} → ${endTime}`;
                }

                timeElement.textContent = timeText;

                content.appendChild(timeElement);
            }

            card.appendChild(content);

            return {
                domNodes: [card]
            };
        },

        // =====================================================
        // CLIC SUR UN ÉVÉNEMENT
        // =====================================================

        eventClick: function (info) {

            info.jsEvent.preventDefault();

            const event = info.event;

            // -------------------------------------------------
            // SI UNE MODALE EXISTE DANS INDEX.HTML
            // -------------------------------------------------

            const modal =
                document.getElementById("event-modal");

            if (modal) {

                const modalTitle =
                    modal.querySelector(".modal-content h2");

                const modalDate =
                    modal.querySelector(".modal-date");

                const modalDescription =
                    modal.querySelector(".modal-description");

                const modalImage =
                    modal.querySelector(".modal-image");

                if (modalTitle) {
                    modalTitle.textContent =
                        event.title;
                }

                if (modalDescription) {
                    modalDescription.textContent =
                        event.extendedProps.description || "";
                }

                if (modalDate) {

                    let dateText = "";

                    if (event.start) {

                        dateText =
                            event.start.toLocaleString(
                                "fr-FR",
                                {
                                    dateStyle: "full",
                                    timeStyle: "short"
                                }
                            );
                    }

                    modalDate.textContent = dateText;
                }

                if (modalImage) {

                    const imageUrl =
                        event.extendedProps.image_url;

                    if (imageUrl) {

                        modalImage.style.backgroundImage =
                            `url("${imageUrl}")`;

                        modalImage.style.display = "block";

                    } else {

                        modalImage.style.backgroundImage =
                            "";

                        modalImage.style.display = "none";
                    }
                }

                modal.style.display = "block";

                // Bouton Discord
                const discordButton =
                    modal.querySelector(".discord-button");

                if (discordButton) {

                    const discordUrl =
                        event.extendedProps.event_url;

                    if (discordUrl) {

                        discordButton.href = discordUrl;
                        discordButton.style.display = "inline-block";

                    } else {

                        discordButton.style.display = "none";
                    }
                }

                return;
            }

            // -------------------------------------------------
            // FALLBACK : OUVERTURE DIRECTE DISCORD
            // -------------------------------------------------

            const discordUrl =
                event.extendedProps.event_url;

            if (discordUrl) {

                window.open(
                    discordUrl,
                    "_blank"
                );
            }
        }
    });

    // ========================================================
    // AFFICHAGE
    // ========================================================

    calendar.render();

    // ========================================================
    // ACTUALISATION AUTOMATIQUE
    // ========================================================

    setInterval(function () {

        console.log(
            "🔄 Actualisation des événements..."
        );

        calendar.refetchEvents();

    }, 30000);

    function formatStatus(status) {
    
    const existingStatus =
    modal.querySelector(".modal-status");

    if (existingStatus) {

    existingStatus.textContent =
        formatStatus(event.extendedProps.status);
    }

    switch (status) {

        case "EventStatus.scheduled":
            return "🟢 Programmé";

        case "EventStatus.active":
            return "🔴 En cours";

        case "EventStatus.completed":
            return "⚪ Terminé";

        case "EventStatus.cancelled":
            return "❌ Annulé";

        case "EventStatus.canceled":
            return "❌ Annulé";

        default:
            return "ℹ️ " + (status || "Inconnu");
        }
    }

    function formatDate(date) {

    if (!date) {
        return "";
    }

    return date.toLocaleDateString(
            "fr-FR",
                {
                    weekday: "long",
                    day: "numeric",
                    month: "long",
                    year: "numeric"
                }
        );
    }
});