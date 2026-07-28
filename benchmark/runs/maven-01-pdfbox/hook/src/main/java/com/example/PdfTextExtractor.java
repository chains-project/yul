package com.example;

import org.apache.pdfbox.Loader;
import org.apache.pdfbox.pdmodel.PDDocument;
import org.apache.pdfbox.text.PDFTextStripper;

import java.io.File;
import java.io.IOException;

public class PdfTextExtractor {

    public static void main(String[] args) throws IOException {
        if (args.length != 1) {
            System.err.println("Usage: PdfTextExtractor <path-to-pdf>");
            System.exit(1);
        }

        File pdfFile = new File(args[0]);
        try (PDDocument document = Loader.loadPDF(pdfFile)) {
            PDFTextStripper stripper = new PDFTextStripper();
            System.out.println(stripper.getText(document));
        }
    }
}
