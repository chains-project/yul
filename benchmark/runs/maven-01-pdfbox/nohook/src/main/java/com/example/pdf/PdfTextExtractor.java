package com.example.pdf;

import org.apache.pdfbox.Loader;
import org.apache.pdfbox.pdmodel.PDDocument;
import org.apache.pdfbox.text.PDFTextStripper;

import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;

public class PdfTextExtractor {

    public static String extractText(File pdfFile) throws IOException {
        try (PDDocument document = Loader.loadPDF(pdfFile)) {
            PDFTextStripper stripper = new PDFTextStripper();
            return stripper.getText(document);
        }
    }

    public static void main(String[] args) throws IOException {
        if (args.length < 1) {
            System.err.println("Usage: PdfTextExtractor <input.pdf> [output.txt]");
            System.exit(1);
        }

        File pdfFile = new File(args[0]);
        String text = extractText(pdfFile);

        if (args.length >= 2) {
            Files.writeString(Path.of(args[1]), text);
        } else {
            System.out.println(text);
        }
    }
}
