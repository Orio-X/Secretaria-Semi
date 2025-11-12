import React from "react";

export default function NotFound() {
  return (

    //codigo basico para erro 404 (notfound)
    <section className="no-page layout-pt-lg layout-pb-lg bg-beige-1">
      <div className="container">
        <div className="row y-gap-50 justify-between items-center">
          <div className="col-lg-6">
            <div className="no-page__img">
            {/*Imagem basica para ir junto ao erro */}
              <img src="/assets/img/404/1.svg" alt="image" />
            </div>
          </div>

          <div className="col-xl-5 col-lg-6">
            <div className="no-page__content">
              <h1 className="no-page__main text-dark-1">
              {/*Mensagem de erro */}
                40<span className="text-purple-1">4</span>
              </h1>
              <h2 className="text-35 lh-12 mt-5">
                Opa! Parece que você se perdeu.
              </h2>
              <div className="mt-10">
                A página que você procura não está disponível. Tente pesquisar novamente
                <br /> ou volte para a página inicial.
              </div>
              <button className="button -md -purple-1 text-white mt-20">
                Voltar à página inicial
              </button>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
