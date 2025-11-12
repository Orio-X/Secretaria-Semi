// src/components/ScreenshotWrapper.jsx

import React, { useRef } from 'react';
import html2canvas from 'html2canvas';

/**
 * Um componente que "embrulha" outro conteúdo (children)
 * e fornece um botão para baixar um screenshot desse conteúdo.
 * * @param {object} props
 * @param {React.ReactNode} props.children - O conteúdo que vai ser baixado
 * @param {string} props.filename - O nome do arquivo a ser baixado (ex: "relatorio.png").
 */
const ScreenshotWrapper = ({ children, filename = "screenshot.png" }) => {
    
    // Criamos uma 'ref' para saber qual elemento do DOM queremos capturar
    const contentRef = useRef(null);

    // Função que e chamada pelo botão
    const handleCaptureClick = () => {
        // Verifica se a 'ref' está anexada a um elemento
        if (!contentRef.current) {
            console.error("Erro: A 'ref' do conteúdo não foi encontrada.");
            return;
        }

        console.log("Iniciando captura de tela...");

        // Biblioteca utilizada para fazer o download da imagem
        html2canvas(contentRef.current, {
            // Opção para tentar carregar imagens de outros domínios (pode precisar de config de CORS)
            useCORS: true, 
        }).then((canvas) => {
            // 'canvas' é a imagem desenhada
            
            // link temporario
            const link = document.createElement('a');
            
            // Define o nome do arquivo que será baixado
            link.download = filename;
            
            // Converte o 'canvas' para uma imagem PNG
            link.href = canvas.toDataURL('image/png');
            
            // simula um click para iniciar o download
            link.click();
            
            console.log("Download do screenshot iniciado.");
        }).catch((err) => {
            console.error("Erro ao capturar a tela:", err);
        });
    };

    return (
        <div>
            {/* O Botão para baixar */}
            <button onClick={handleCaptureClick}>
                Baixar como Imagem
            </button>
            
            <hr style={{ margin: '10px 0' }} />

            {/* 7O conteúdo a ser capturado é embrulhado pela div com a 'ref' */}
            <div ref={contentRef}>
                {children}
            </div>
        </div>
    );
};

export default ScreenshotWrapper;