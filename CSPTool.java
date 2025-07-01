import java.io.File;
import java.util.ArrayList;
import java.util.List;
import java.util.stream.Stream;

public class CSPTool {

    public static class Attribute {
        String name;
        String value;

        public Attribute(String name, String value) {
            this.name = name;
            this.value = value;
        }

        @Override
        public String toString() {
            return name + "=\"" + value + "\"";
        }
    }

    public static class Tag {
        String name;
        List<Attribute> attributes;

        public Tag(String name, List<Attribute> attributes) {
            this.name = name;
            this.attributes = attributes;
        }

        @Override
        public String toString() {
            return "<" + name + ">";
        }

        public String getId() {
            for (Attribute attr : attributes) {
                if ("id".equalsIgnoreCase(attr.name)) {
                    return attr.value;
                }
            }
            return "";
        }
    }

    static List<String> eventAttributes = java.util.Arrays.asList(
            "onclick", "ondblclick", "onmousedown", "onmouseup", "onmouseover",
            "onmousemove", "onmouseout", "onmouseenter", "onmouseleave",
            "onkeydown", "onkeypress", "onkeyup", "onfocus", "onblur", "onchange",
            "onsubmit", "onreset", "onselect", "oninput", "onload", "onunload");

    public static List<File> getAllJspFiles(File folder) {
        List<File> jspFiles = new ArrayList<>();
        File[] files = folder.listFiles();
        if (files != null) {
            for (File file : files) {
                if (file.isDirectory()) {
                    jspFiles.addAll(getAllJspFiles(file));
                } else if (file.isFile() && file.getName().endsWith(".jsp")) {
                    jspFiles.add(file);
                }
            }
        }
        return jspFiles;
    }

    public static boolean hasEventAttributes(File htmlFile) {
        try (Stream<String> lines = java.nio.file.Files.lines(htmlFile.toPath())) {
            return lines.anyMatch(line -> eventAttributes.stream()
                    .anyMatch(attr -> line.toLowerCase().contains(attr + "=")));
        } catch (Exception e) {
            return false;
        }
    }

    public static List<Tag> listAllTagsAndAttributes(File htmlFile) throws Exception {
        List<Tag> result = new ArrayList<>();
        try {
            String content = new String(java.nio.file.Files.readAllBytes(htmlFile.toPath()));
            java.util.regex.Pattern tagPattern = java.util.regex.Pattern.compile("<(\\w+)([^>]*)>");
            java.util.regex.Matcher tagMatcher = tagPattern.matcher(content);

            while (tagMatcher.find()) {
                String tagName = tagMatcher.group(1);
                String attrString = tagMatcher.group(2);

                String attrName = "";
                String attrValue = "";
                List<Attribute> attributes = new ArrayList<>();

                java.util.regex.Pattern attrPattern = java.util.regex.Pattern.compile("(\\w+)\\s*=\\s*(['\"])(.*?)\\2");
                java.util.regex.Matcher attrMatcher = attrPattern.matcher(attrString);

                List<String> attrs = new ArrayList<>();
                while (attrMatcher.find()) {
                    attrName = attrMatcher.group(1);
                    attrValue = attrMatcher.group(3);

                    if (eventAttributes.contains(attrName.toLowerCase())
                            || attrName.equalsIgnoreCase("id")) {
                        attrs.add(attrName + "=\"" + attrValue + "\"");
                        attributes.add(new Attribute(attrName, attrValue));
                    } else {
                        continue; // Skip attributes not in eventAttributes
                    }
                }

                if (attrs.isEmpty()) {
                } else {
                    if (attrs.stream().anyMatch(
                            attr -> eventAttributes.stream().anyMatch(eventAttr -> attr.startsWith(eventAttr + "=")))) {
                        result.add(new Tag(tagName, attributes));
                    }
                }
            }
        } catch (Exception e) {
            // Handle exception or log
        }
        return result;
    }

    public static void deleteDirectoryRecursively(File dir) throws Exception {
        if (dir.isDirectory()) {
            File[] entries = dir.listFiles();
            if (entries != null) {
                for (File entry : entries) {
                    deleteDirectoryRecursively(entry);
                }
            }
        }
        if (!dir.delete()) {
            throw new Exception("Failed to delete " + dir.getAbsolutePath());
        }
    }

    public static void main(String[] args) {
        String folderPath = "F:\\DXC\\Projects\\IMS\\ims_dev_arcgis4\\WebContent"; // Change this to your folder path
        String jsFolderPath = "F:\\DXC\\Projects\\IMS\\ims_dev_arcgis4\\WebContent\\csp"; // Change this to your JS
                                                                                          // folder path

        // Get all JSP files in the specified folder and its subfolders
        List<File> jspFiles = getAllJspFiles(new File(folderPath));
        int totalFilesWithEventAttributes = 0;
        for (File f : jspFiles) {
            if (hasEventAttributes(f)) {
                System.out.println("File with event attributes: " + f.getAbsolutePath());
                totalFilesWithEventAttributes += 1;
            }
        }

        // Print the total number of files with event attributes
        System.out.println("Total files with event attributes: " + totalFilesWithEventAttributes);

        /*

        // List all tags and attributes in JSP files

        // Delte js folder if it exists
        File jsFolder = new File(jsFolderPath);
        if (jsFolder.exists()) {
            try {
                deleteDirectoryRecursively(jsFolder);
                System.out.println("Deleted existing JS folder: " + jsFolderPath);
            } catch (Exception e) {
                e.printStackTrace();
                System.out.println("Error deleting JS folder: " + jsFolderPath);
            }
        }

        // Create a new JS folder
        if (!jsFolder.exists()) {
            jsFolder.mkdirs();
            System.out.println("Created JS folder: " + jsFolderPath);
        }

        for (File jspFile : jspFiles) {
            List<Tag> allTagsAndAttributes = new ArrayList<>();
            try {
                allTagsAndAttributes = listAllTagsAndAttributes(jspFile);
                for (Tag tag : allTagsAndAttributes) {
                    System.out.println(tag.name + " " + tag.attributes);
                }

                // Create a new file to add Event attributes
                String jsFileName = jspFile.getName().replace(jspFile.getName(),
                        jspFile.getName().replace(".jsp", "") + "_Events.js");
                File jsFile = new File(jsFolderPath, jsFileName);
                if (!jsFile.exists()) {
                    jsFile.createNewFile();
                }

                // Write event listeners to the JS file
                try (java.io.FileWriter writer = new java.io.FileWriter(jsFile)) {

                    // Prepare event listeners
                    String firstLine = "document.addEventListener('DOMContentLoaded', function() {\n";
                    String content = "";
                    String lastLine = "});\n";

                    for (Tag tag : allTagsAndAttributes) {
                        for (Attribute attr : tag.attributes) {
                            if (eventAttributes.contains(attr.name)) {
                                content += "    document.getElementById('" + tag.getId() + "').addEventListener("
                                        + "\"" + attr.name.toLowerCase().replace("on", "") + "\", "
                                        + attr.value.replace("()", "").replace(";", "") + ");\n";
                            }
                        }
                    }

                    // Write to the JS file
                    writer.write(firstLine);
                    writer.write(content);
                    writer.write(lastLine);
                    System.out.println("Event listeners written to: " + jsFile.getAbsolutePath());
                } catch (Exception e) {
                    e.printStackTrace();
                    System.out.println("Error writing to JS file: " + jsFile.getAbsolutePath());
                }

                // Open the jsp file and include the JS file
                /*try (java.io.FileWriter writer = new java.io.FileWriter(jsFile)) {

                    // Read the JSP file content
                    String jspContent = new String(java.nio.file.Files.readAllBytes(jspFile.toPath()));
                    // Insert the script tag before </head>
                    int headCloseIndex = jspContent.toLowerCase().indexOf("</head>");
                    if (headCloseIndex != -1) {
                        String beforeHead = jspContent.substring(0, headCloseIndex);
                        String afterHead = jspContent.substring(headCloseIndex);
                        writer.write(beforeHead);
                        writer.write("<script src=\"" + "csp\\" + jsFileName + "\"></script>\n");
                        writer.write(afterHead);

                        System.out.println("JS file included in JSP: " + jspFile.getAbsolutePath());
                    }
                } catch (Exception e) {
                    e.printStackTrace();
                    System.out.println("Error including JS file in JSP: " + jspFile.getAbsolutePath());
                }
            } catch (Exception e) {
                e.printStackTrace();
                System.out.println("Tags and attributes in the first JSP file:");
            }
             */
        }
        
    }

