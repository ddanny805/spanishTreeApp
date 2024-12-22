$(document).ready(function () {
    $("#generate").click(function () {
        const sentence = $("#sentence").val();
        $("#breakdown").text("Generando análisis...");
        $("#tree-container").html("<p>Generando árbol...</p>");
        $.ajax({
            url: "/generate",
            method: "POST",
            contentType: "application/json; charset=utf-8",
            headers: {
                "Cache-Control": "no-store, no-cache, must-revalidate"
            },
            data: JSON.stringify({ sentence }),
            success: function (response) {
                if (response.breakdown && response.tree) {
                    $("#breakdown").text(response.breakdown);
                    $("#tree-container").html(response.tree); // Inject SVG
                } else {
                    $("#breakdown").text("Error: No se pudo generar el análisis.");
                    $("#tree-container").text("Error: No se pudo generar el árbol.");
                }
            },
            error: function () {
                $("#breakdown").text("Error: No se pudo generar el análisis.");
                $("#tree-container").text("Error: No se pudo generar el árbol.");
            },
        });
    });
});
