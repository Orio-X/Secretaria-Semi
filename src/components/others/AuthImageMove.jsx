import gsap from "gsap"; // Importa a biblioteca GSAP para animações
import React, { useEffect } from "react";

export default function AuthImageMove() {
  // Função que previne o comportamento padrão de formulários (não utilizada no JSX)
  const handleSubmit = (e) => {
    e.preventDefault();
  };
  
  // Efeito que configura o efeito Parallax (movimento das imagens com o mouse)
  useEffect(() => {
    const parallaxIt = () => {
      // Seleciona todos os contêineres que ativam o efeito (deve ser o pai das imagens)
      const target = document.querySelectorAll(".js-mouse-move-container");

      target.forEach((container) => {
        // Seleciona as imagens que devem se mover dentro de cada contêiner
        const targets = container.querySelectorAll(".js-mouse-move");

        targets.forEach((el) => {
          // Obtém a intensidade do movimento a partir do atributo 'data-move'
          const movement = el.getAttribute("data-move");

          // Adiciona um listener de evento para o movimento do mouse no documento inteiro
          document.addEventListener("mousemove", (e) => {
            // Calcula a posição do mouse em relação ao contêiner
            const relX = e.pageX - container.offsetLeft;
            const relY = e.pageY - container.offsetTop;

            // Usa GSAP para animar a posição (x e y) do elemento
            gsap.to(el, {
              // Calcula a nova posição X com base na posição do mouse e na intensidade ('data-move')
              x:
                ((relX - container.offsetWidth / 2) / container.offsetWidth) *
                Number(movement),
              // Calcula a nova posição Y com base na posição do mouse e na intensidade ('data-move')
              y:
                ((relY - container.offsetHeight / 2) / container.offsetHeight) *
                Number(movement),
              duration: 0.2, // Duração suave da animação
            });
          });
        });
      });
    };

    // Inicia a função de parallax
    parallaxIt();
  }, []); // O array vazio assegura que o efeito rode apenas na montagem
  
  return (
    // Contêiner principal da imagem de fundo. **NOTA:** A classe `.js-mouse-move-container` está faltando aqui, mas é essencial para o JS funcionar.
    <div 
      className="form-page__img bg-dark-1 js-mouse-move-container" 
      style={{
        // A altura de '1000vh' parece um erro de digitação/configuração, normalmente seria '100vh' ou a altura do contêiner pai.
        height: '1000vh',
        overflow: 'hidden'
      }}
    >
      <div className="form-page-composition">
        {/* Elemento de fundo (mais distante - data-move="50") */}
        <div className="-el-3">
          <img
            style={{ width: "200%" }}
            data-move="50" // Intensidade do movimento Parallax
            className="js-mouse-move" // Se move com o mouse
            src="/assets/img/login/bg.png"
            alt="bg"
          />
        </div>
        
        {/* Elemento intermediário (movimento médio - data-move="20") */}
        <div 
          className="-el-1" 
          style={{ 
            transform: 'translateY(-5px)', 
          }}
        >
          <img
            style={{ width: "100%" }}
            data-move="20" // Movimento menor que o fundo
            className="js-mouse-move"
            src="/assets/img/home-9/hero/8.png"
            alt="image"
          />
        </div>
        
        {/* Elemento mais próximo (menor movimento - data-move="10") */}
        <div 
          className="-el-2" 
          style={{ 
            transform: 'translateY(-55px)', 
          }}
        > 
          <img
            data-move="10" // Menor movimento, parece mais próximo
            className="js-mouse-move"
            src="/assets/img/home-9/hero/1.png"
            alt="icon"
          />
        </div>

      </div>
    </div>
  );
}