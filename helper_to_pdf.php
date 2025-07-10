<?php

if (!defined('BASEPATH'))
    exit('No direct script access allowed');

function pdf_create($html, $filename, $orientation = 'P', $size = 'A4', $L = 15, $T = 15, $B = 15) {
    include_once ('tcpdf/tcpdf.php');
    /*     * Configurando pagina pdf* */
    $pdf = new TCPDF($orientation, 'mm', $size);
    $pdf->setPrintHeader(false);
    $pdf->setPrintFooter(false);
    $pdf->SetDisplayMode('real', 'default');
    $pdf->SetFont('helvetica', '', 6);
    //$pdf->Write(0, 'Example of HTML Justification', '', 0, 'L', true, 0, false, false, 0);
    $pdf->SetAutoPageBreak(TRUE, $B);
    $pdf->SetMargins($L, $T);
    $pdf->AddPage();
    $pdf->writeHTML($html, true, 0, true, 0);
    $pdf->Output("tmp/" . $filename . ".pdf", "I");
}

function pdf_create_nuevo($html, $filename, $stream=TRUE, $orientation = 'portrait')
{
    //require_once("dompdf/dompdf_config.inc.php");
    set_time_limit(0);
    ini_set('memory_limit','512M');
    
    $dompdf = new DOMPDF();
    $dompdf->load_html($html);
    $dompdf->set_paper('letter', $orientation);
    $dompdf->render();
    if ($stream) {
        $dompdf->stream($filename.".pdf");
    } else {
        $CI =& get_instance();
        $CI->load->helper('file');
        write_file("./temp/pdf_$filename.pdf", $dompdf->output());
    }
}

function pdf_create_acta($html, $filename, $orientation = 'P', $size = 'Letter', $L = 15, $T = 15, $B = 15, $logo = false) {
    include_once ('TCPDF/tcpdf.php');
    $pdf = new TCPDF(PDF_PAGE_ORIENTATION, PDF_UNIT, PDF_PAGE_FORMAT, true, 'UTF-8', false);
    $pdf->SetHeaderData(false, false, false . '', false);
    $pdf->AddPage();
    $pdf->writeHTML($html, true, 0, true, 0);
    ob_end_clean();
    $pdf->Output("tmp/" . $filename . ".pdf", "I");
}

?>
