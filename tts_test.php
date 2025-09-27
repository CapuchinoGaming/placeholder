<!--
This .php page should run a Python file.
The Python file should run a text-to-voice API to turn the "paragraph" into voice.
In the future, I would like to have the "paragraph" be part of Python instead of being hardcoded.
-->

<html>
    <head>
        <title>Oracle - TTS Testing</title>
        <!-- <link rel="stylesheet" href="styleinfo.css"/> -->
    </head>
    
    <body>

        <main>
            <!-- Heading -->
            <h3>TTS Testing Page</h3>

            <!-- Description -->
            <p>Genai should be able to turn the following paragraph into speech:</p>
            <p>---------------------------------------------------</p>
            <p>Roblox is love, Roblox is life</p>
        </main>

    </body>
</html>

<?php
    // Run Python file
    echo "<pre>";
    echo shell_exec("python tts_script.py");  // or "python3 --version"
    echo "</pre>";
?>