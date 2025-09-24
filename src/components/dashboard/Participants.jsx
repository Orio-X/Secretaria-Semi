import React, { useState, useEffect } from "react";
import FooterNine from "../layout/footers/FooterNine";
import PageLinksTwo from "../common/PageLinksTwo";
import { letters } from "@/data/dictionary";

export default function Participants() {
  const [currentLetter, setCurrentLetter] = useState("A");
  const [participants, setParticipants] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchAllParticipants() {
      setLoading(true);

      //Definição dos 3 endpoints que já possui
      const urls = [
        "http://127.0.0.1:8000/api/professores/",
        "http://127.0.0.1:8000/api/alunos/",
        "http://127.0.0.1:8000/api/responsaveis/",
      ];

      try {
        //todas as requisições em paralelo
        const responses = await Promise.all(urls.map(url => fetch(url)));
        
        // Verificar se todas as requisições foram bem sucedidas
        for (const res of responses) {
            if (!res.ok) {
                throw new Error(`HTTP error! status: ${res.status} for URL: ${res.url}`);
            }
        }

        const [professores, alunos, responsaveis] = await Promise.all(responses.map(res => res.json()));

        //Normalizar e Juntar os dados em uma única lista
        const combinedList = [];

        // Adiciona professores, padronizando o objeto
        professores.forEach(prof => {
          combinedList.push({
            id: `prof-${prof.id}`, // Adiciona um prefixo para garantir ID único
            nome: prof.nome,
            email: prof.email,
            foto: prof.foto,
            tipo: "Professor",
          });
        });

        // Adiciona alunos, lidando com os nomes de campos diferentes (name_aluno)
        alunos.forEach(aluno => {
          combinedList.push({
            id: `aluno-${aluno.id}`,
            nome: aluno.name_aluno, 
            email: aluno.email_aluno, 
            foto: aluno.foto,
            tipo: "Aluno",
          });
        });

        // Adiciona responsáveis
        responsaveis.forEach(resp => {
          combinedList.push({
            id: `resp-${resp.id}`,
            nome: resp.nome,
            email: resp.email,
            foto: resp.foto,
            tipo: "Responsável",
          });
        });
        
        //Ordena a lista final por nome
        combinedList.sort((a, b) => (a.nome || "").localeCompare(b.nome || ""));

        setParticipants(combinedList);

      } catch (error) {
        console.error("Erro ao buscar participantes:", error);
      } finally {
        setLoading(false);
      }
    }

    fetchAllParticipants();
  }, []); // O array vazio garante que a busca ocorre apenas uma vez.

  return (
    <div className="dashboard__main">
        <div className="dashboard__content bg-light-4">
          <div className="row pb-50 mb-10">
            <div className="col-auto">
              <h1 className="text-30 lh-12 fw-700">Participants</h1>
              <PageLinksTwo />
            </div>
          </div>
  
          <div className="row y-gap-30">
            <div className="col-12">
              <div className="rounded-16 bg-white -dark-bg-dark-1 shadow-4 h-100">
                <div className="d-flex items-center py-20 px-30 border-bottom-light">
                  <h2 className="text-17 lh-1 fw-500">Lista de Participantes</h2>
                </div>
  
                <div className="py-30 px-30">
                  <div className="text-18 fw-500 text-dark-1 lh-12 mt-10">
                    Filtrar por inicial do nome
                  </div>
                  <div className="d-flex x-gap-10 y-gap-10 flex-wrap pt-20">
                    <div>
                      <div
                        className={`py-8 px-10 d-flex justify-center items-center cursor-pointer rounded-4 ${
                          currentLetter === "All"
                            ? "bg-dark-1 -dark-bg-dark-2 text-white"
                            : "border-light"
                        }`}
                        onClick={() => setCurrentLetter("All")}
                      >
                        All
                      </div>
                    </div>
                    {letters.map((elm, i) => (
                      <div
                        key={i}
                        className={`size-35 d-flex justify-center items-center border-light rounded-4 cursor-pointer ${
                          currentLetter === elm
                            ? "bg-dark-1 -dark-bg-dark-2 text-white"
                            : ""
                        }`}
                        onClick={() => setCurrentLetter(elm)}
                      >
                        {elm}
                      </div>
                    ))}
                  </div>
  
                  <div className="mt-40">
                    <div className="px-30 py-20 bg-light-7 -dark-bg-dark-2 rounded-8">
                      <div className="row x-gap-10">
                        <div className="col-lg-5">
                          <div className="text-purple-1">Nome / Email</div>
                        </div>
                        <div className="col-lg-2">
                          <div className="text-purple-1">Tipo</div>
                        </div>
                        <div className="col-lg-2">
                          <div className="text-purple-1">Grupos</div>
                        </div>
                        <div className="col-lg-3">
                          <div className="text-purple-1">Último acesso</div>
                        </div>
                      </div>
                    </div>
  
                    {loading ? (
                      <div className="px-30 py-20">Carregando participantes...</div>
                    ) : participants.length === 0 ? (
                      <div className="px-30 py-20">
                        Nenhum participante encontrado.
                      </div>
                    ) : (
                      participants
                        .filter((elm) =>
                          currentLetter === "All"
                            ? true
                            : elm.nome?.startsWith(currentLetter)
                        )
                        .map((elm) => ( //Usar elm.id como key 
                          <div key={elm.id} className="px-30 border-bottom-light">
                            <div className="row x-gap-10 items-center py-15">
                              <div className="col-lg-5">
                                <div className="d-flex items-center">
                                  <img
                                    src={elm.foto || "/img/default-user.png"}
                                    alt="foto"
                                    className="size-40 fit-cover rounded-full"
                                  />
                                  <div className="ml-10">
                                    <div className="text-dark-1 lh-12 fw-500">
                                      {elm.nome}
                                    </div>
                                    <div className="text-14 lh-12 mt-5">
                                      {elm.email || "sem e-mail"}
                                    </div>
                                  </div>
                                </div>
                              </div>
                              <div className="col-lg-2">{elm.tipo}</div>
                              <div className="col-lg-2">—</div>
                              <div className="col-lg-3">—</div>
                            </div>
                          </div>
                        ))
                    )}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        <FooterNine />
    </div>
  );
}