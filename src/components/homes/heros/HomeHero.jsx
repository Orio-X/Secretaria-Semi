import gsap from "gsap";
import { Link } from "react-router-dom";
import { ShapeRendering } from "../../../svg/index";
import React, { useEffect } from "react";

//Aqui serve para modifcar as frases na pagina inicial, a principal quando voce abre o site
// Itens removidos conforme solicitado.
const masthead_info = [];

const hero_content = {
  title: "Gerencie com a habilidade dos ",
  text_underline: "Melhores",
  info_hero: (
    <>
      Gerencie sua escola de forma eficiente e prática com nosso site,
      <br /> otimizando processos e facilitando a comunicação com alunos e
      professores.
    </>
  ),
  starts: [
    "icon-star text-yellow-1 text-11",
    "icon-star text-yellow-1 text-11",
    "icon-star text-yellow-1 text-11",
    "icon-star text-yellow-1 text-11",
    "icon-star text-yellow-1 text-11",
  ],
};
const { title, text_underline, info_hero, starts } = hero_content;

const HomeHero = () => {
  useEffect(() => {
    const parallaxIt = () => {
      const target = document.querySelectorAll(".js-mouse-move-container");

      target.forEach((container) => {
        const targets = container.querySelectorAll(".js-mouse-move");

        targets.forEach((el) => {
          const movement = el.getAttribute("data-move");

          document.addEventListener("mousemove", (e) => {
            const relX = e.pageX - container.offsetLeft;
            const relY = e.pageY - container.offsetTop;

            gsap.to(el, {
              x:
                ((relX - container.offsetWidth / 2) / container.offsetWidth) *
                Number(movement),
              y:
                ((relY - container.offsetHeight / 2) / container.offsetHeight) *
                Number(movement),
              duration: 0.2,
            });
          });
        });
      });
    };

    parallaxIt();
  }, []);

  return (
    <>
      <section className="masthead -type-1 js-mouse-move-container">
        <div className="masthead__bg">
          {/* Imagem mantida: bg.png */}
          <img src={"/assets/img/home-1/hero/bg.png"} alt="image" />
        </div>

        <div className="container">
          <div className="row y-gap-30 justify-between items-end">
            <div className="col-xl-6 col-lg-6 col-sm-10">
              <div
                className="masthead__content"
                data-aos="fade-up"
                data-aos-delay="500"
              >
                <h1 className="masthead__title">
                  {title}{" "}
                  <span className="text-green-1 underline">
                    {text_underline}
                  </span>
                </h1>
                <p
                  data-aos="fade-up"
                  data-aos-duration="100"
                  className="masthead__text"
                >
                  {info_hero}
                </p>
                <div
                  data-aos="fade-up"
                  data-aos-duration="200"
                  className="masthead__buttons row x-gap-10 y-gap-10"
                >
                  <div className="col-12 col-sm-auto">
                    <Link
                      data-barba
                      to="/login"
                      className="button -md -purple-1 text-white"
                    >
                      Acessar plataforma
                    </Link>
                  </div>
                  <div className="col-12 col-sm-auto"></div>
                </div>
                <div
                  data-aos="fade-up"
                  data-aos-duration="300"
                  className="masthead-info row y-gap-15 sm:d-none"
                >
                  {/* O array 'masthead_info' está vazio, então nada será renderizado aqui. */}
                  {masthead_info.map((item, i) => (
                    <div
                      key={i}
                      className="masthead-info__item d-flex items-center text-white"
                    >
                      <div className="masthead-info__icon mr-10">
                        <img src={item.icon} alt="icon" />
                      </div>
                      <div className="masthead-info__title lh-1">
                        {item.text}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            <div
              className="col-xl-6 col-lg-6"
              data-aos="fade-up"
              data-aos-delay="700"
            >
              <div className="masthead-image">
                <div className="masthead-image__el1">
                  {/* Imagem removida: 1.png */}

                  <div
                    data-move="30"
                    className="lg:d-none img-el -w-250 px-20 py-20 d-flex items-center bg-white rounded-8 js-mouse-move"
                  >
                    <div className="size-50 d-flex justify-center items-center bg-red-2 rounded-full">
                      {/* Imagem mantida: 1.svg */}
                      <img src={"/assets/img/masthead/1.svg"} alt="icon" />
                    </div>
                    <div className="ml-20">
                      <div className="text-orange-1 text-16 fw-500 lh-1">
                        12.000 +
                      </div>
                      <div className="mt-3">Secretarias Cadastradas</div>
                    </div>
                  </div>
                </div>

                <div className="masthead-image__el2">
                  {/* Imagem removida: 2.png */}

                  <div
                    data-move="60"
                    className="lg:d-none img-el -w-260 px-20 py-20 d-flex items-center bg-white rounded-8 js-mouse-move"
                  >
                    {/* Imagem mantida: 4.png */}
                    <img src={"/assets/img/masthead/4.png"} alt="icon" />
                    <div className="ml-20">
                      <div className="text-dark-1 text-15 fw-500 lh-1">
                        Gabriel
                      </div>
                      <div className="mt-3">Diretor do Sesi Garavelo</div>
                      <div className="d-flex x-gap-5 mt-3">
                        {starts.map((start, index) => (
                          <div key={index}>
                            <div className={start}></div>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>

                <div className="masthead-image__el3">
                  {/* Imagem removida: 3.png */}

                  <div
                    data-move="30"
                    className="shadow-4 img-el -w-260 px-30 py-20 d-flex items-center bg-white rounded-8 js-mouse-move"
                  >
                    <div className="img-el__side">
                      <div className="size-50 d-flex justify-center items-center bg-purple-1 rounded-full">
                        {/* Imagem mantida: 2.svg */}
                        <img
                          style={{ objectFit: "cover" }}
                          src={"/assets/img/masthead/2.svg"}
                          alt="icon"
                        />
                      </div>
                    </div>
                    <div className="">
                      <div className="text-purple-1 text-16 fw-500 lh-1">
                        Selo de Qualidade
                      </div>
                      <div className="mt-3">A melhor plataforma de gestão escolar.</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* animated shape start */}
        <ShapeRendering />
        {/* animated shape end */}
      </section>
    </>
  );
};

export default HomeHero;