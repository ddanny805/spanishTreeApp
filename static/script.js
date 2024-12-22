$(document).ready(function () {
    // Automatically adjust the height of the textarea as the user types
    $("#sentence").on("input", function () {
        $(this).css("height", "auto").css("height", this.scrollHeight + "px");
    });

    // Generate button functionality
    $("#generate").click(function () {
        const sentence = $("#sentence").val();
        $("#breakdown").text("Generando análisis...");
        $("#tree-container").html("<p>Generando árbol...</p>");
        
        // Check if the sentence is not empty before making the request
        if (!sentence.trim()) {
            $("#breakdown").text("Por favor ingresa una oración.");
            $("#tree-container").empty();
            return;
        }

        $.ajax({
            url: "/generate",
            method: "POST",
            contentType: "application/json",
            data: JSON.stringify({ sentence }),
            success: function (response) {
                if (response.breakdown && response.tree) {
                    $("#breakdown").text(response.breakdown);
                    $("#tree-container").html(response.tree); // Inject SVG
                } else {
                    $("#breakdown").text("Error: No se pudo generar el análisis.");
                    $("#tree-container").html("<p>Error: No se pudo generar el árbol.</p>");
                }
            },
            error: function () {
                $("#breakdown").text("Error: No se pudo generar el análisis.");
                $("#tree-container").html("<p>Error: No se pudo generar el árbol.</p>");
            },
        });
    });
});
