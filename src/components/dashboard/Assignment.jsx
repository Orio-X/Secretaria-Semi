import React, { useState, useEffect } from "react";
import { useParams, Link } from "react-router-dom";
import axios from "axios";
import FooterNine from "../layout/footers/FooterNine";
import PageLinksTwo from "../common/PageLinksTwo";

// Função auxiliar para formatar a data
const formatarData = (dataString) => {
  const data = new Date(dataString + 'T00:00:00'); // Adiciona T00:00:00 para evitar problemas de fuso horário
  const options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric', hour: 'numeric', minute: 'numeric' };
  return data.toLocaleDateString('pt-BR', options);
};

// Função auxiliar para calcular o tempo restante
const calcularTempoRestante = (dataEntrega) => {
  if (!dataEntrega) return "Sem data de entrega";
  
  const agora = new Date();
  const entrega = new Date(dataEntrega + 'T23:59:59'); // Considera o final do dia da entrega
  const diffEmMs = entrega - agora;

  if (diffEmMs < 0) {
    return "Tarefa vencida";
  }

  const diffEmDias = Math.ceil(diffEmMs / (1000 * 60 * 60 * 24));
  if (diffEmDias <= 1) {
    return "A tarefa vence hoje";
  }
  return `${diffEmDias} dias restantes`;
};

export default function Assignment() {
  const { tarefaId } = useParams(); // Pega o ID da tarefa da URL
  const [tarefa, setTarefa] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchTarefa = async () => {
      const token = localStorage.getItem('authToken');
      if (!token) {
        setError("Autenticação necessária.");
        setLoading(false);
        return;
      }

      try {
        const response = await axios.get(`/api/tarefas/${tarefaId}/`, {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        setTarefa(response.data);
      } catch (err) {
        setError("Não foi possível carregar a tarefa.");
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchTarefa();
  }, [tarefaId]); // Re-executa se o ID na URL mudar

  if (loading) {
    return <div className="dashboard__main"><div className="dashboard__content"><p>Carregando tarefa...</p></div></div>;
  }

  if (error) {
    return <div className="dashboard__main"><div className="dashboard__content"><p style={{color: 'red'}}>{error}</p></div></div>;
  }

  if (!tarefa) {
    return <div className="dashboard__main"><div className="dashboard__content"><p>Tarefa não encontrada.</p></div></div>;
  }

  // --- O JSX abaixo é o seu layout, agora preenchido com dados dinâmicos ---
  return (
    <div className="dashboard__main">
      <div className="dashboard__content bg-light-4">
        <div className="row pb-50 mb-10">
          <div className="col-auto">
            <h1 className="text-30 lh-12 fw-700">{tarefa.titulo}</h1>
            <PageLinksTwo />
          </div>
        </div>

        <div className="row y-gap-30">
          <div className="col-xl-10">
            <div className="rounded-16 bg-white -dark-bg-dark-1 shadow-4 h-100">
              <div className="d-flex items-center py-20 px-30 border-bottom-light">
                <h2 className="text-17 lh-1 fw-500">Detalhes da Tarefa</h2>
              </div>

              <div className="py-30 px-30">
                <div>
                  <h4 className="text-18 lh-1 fw-500">{tarefa.titulo}</h4>
                  <div className="col-xl-6">
                    <p className="mt-15">
                      {tarefa.descricao || "Esta tarefa não possui uma descrição detalhada."}
                    </p>
                  </div>
                </div>

                <div className="mt-60">
                  <h4 className="text-18 lh-1 fw-500">Resumo de Avaliação</h4>
                </div>

                <div className="mt-30">
                  {/* AVISO: Os dados abaixo (Participantes, Enviado, etc.) são estáticos. */}
                  {/* Veja a explicação no final sobre como torná-los dinâmicos. */}
                  <div className="rounded-8 px-25 py-25 bg-light-4">
                    <div className="row"><div className="col-3"><div className="text-dark-1">Oculto para os estudantes</div></div><div className="col-auto">Não</div></div>
                  </div>
                  <div className="rounded-8 px-25 py-25 "><div className="row"><div className="col-3"><div className="text-dark-1">Participantes</div></div><div className="col-auto">10</div></div></div>
                  <div className="rounded-8 px-25 py-25 bg-light-4"><div className="row"><div className="col-3"><div className="text-dark-1">Enviado</div></div><div className="col-auto">2</div></div></div>
                  <div className="rounded-8 px-25 py-25 "><div className="row"><div className="col-3"><div className="text-dark-1">Precisa de avaliação</div></div><div className="col-auto">1</div></div></div>
                  
                  {/* Data de entrega e tempo restante agora são dinâmicos */}
                  <div className="rounded-8 px-25 py-25 bg-light-4">
                    <div className="row">
                      <div className="col-3"><div className="text-dark-1">Data de entrega</div></div>
                      <div className="col-auto">{tarefa.data_entrega ? formatarData(tarefa.data_entrega) : "Não definida"}</div>
                    </div>
                  </div>
                  <div className="rounded-8 px-25 py-25 ">
                    <div className="row">
                      <div className="col-3"><div className="text-dark-1">Tempo restante</div></div>
                      <div className="col-auto">{calcularTempoRestante(tarefa.data_entrega)}</div>
                    </div>
                  </div>
                </div>

                <div className="d-flex x-gap-30 flex-wrap y-gap-10 justify-center items-center mt-30">
                  <div><Link to="#" className="button -icon -light-3 h-50">Ver todas as submissões<i className="icon-arrow-top-right text-13 ml-10"></i></Link></div>
                  <div><Link to="#" className="button -icon -light-3 h-50">Avaliar<i className="icon-arrow-top-right text-13 ml-10"></i></Link></div>
                </div>
                
                {/* ... o resto do seu layout estático pode continuar aqui ... */}
              </div>
            </div>
          </div>
        </div>
      </div>
      <FooterNine />
    </div>
  );
}