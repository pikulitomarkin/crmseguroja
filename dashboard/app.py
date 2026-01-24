"""
Dashboard CRM com Streamlit
"""
import sys
from pathlib import Path

# Adiciona o diretório raiz ao path
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config.settings import settings
from app.database.models import Lead, ChatMessage
from app.services.database_service import LeadService, MessageService
from app.services.evolution_service import EvolutionService
import asyncio

# Configuração da página
st.set_page_config(
    page_title="CRM Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS customizado
st.markdown("""
<style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .lead-card {
        background-color: white;
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid #25D366;
        margin: 10px 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .status-novo { color: #1f77b4; font-weight: bold; }
    .status-qualificado { color: #2ca02c; font-weight: bold; }
    .status-em_atendimento { color: #ff7f0e; font-weight: bold; }
    .status-finalizado { color: #d62728; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# Inicializa banco de dados
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
)
SessionLocal = sessionmaker(bind=engine)

# State da sessão
if "refresh_key" not in st.session_state:
    st.session_state.refresh_key = 0


def get_db():
    """Retorna sessão do banco de dados"""
    return SessionLocal()


@st.cache_data(ttl=30)
def load_leads():
    """Carrega todos os leads"""
    db = get_db()
    leads = db.query(Lead).all()
    db.close()
    return leads


@st.cache_data(ttl=30)
def load_statistics():
    """Carrega estatísticas"""
    db = get_db()
    
    total = db.query(Lead).count()
    novo = db.query(Lead).filter(Lead.status == "novo").count()
    qualificado = db.query(Lead).filter(Lead.status == "qualificado").count()
    em_atendimento = db.query(Lead).filter(Lead.status == "em_atendimento").count()
    finalizado = db.query(Lead).filter(Lead.status == "finalizado").count()
    
    db.close()
    
    return {
        "total": total,
        "novo": novo,
        "qualificado": qualificado,
        "em_atendimento": em_atendimento,
        "finalizado": finalizado
    }


@st.cache_data(ttl=30)
def load_lead_details(lead_id: int):
    """Carrega detalhes de um lead"""
    db = get_db()
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    
    if lead:
        messages = db.query(ChatMessage).filter(
            ChatMessage.whatsapp_number == lead.whatsapp_number
        ).order_by(ChatMessage.created_at.desc()).limit(100).all()
        messages.reverse()
        db.close()
        return lead, messages
    
    db.close()
    return None, []


def refresh_data():
    """Força refresh dos dados"""
    st.session_state.refresh_key += 1
    st.rerun()


# Header
col1, col2 = st.columns([3, 1])
with col1:
    st.title("📊 CRM Dashboard")
    st.markdown("Sistema de Qualificação de Leads com IA")

with col2:
    if st.button("🔄 Atualizar", key="refresh_btn"):
        refresh_data()

st.divider()

# Seção de Estatísticas
stats = load_statistics()

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric(
        "Total de Leads",
        stats["total"],
        delta="",
        delta_color="off"
    )

with col2:
    st.metric(
        "Novos",
        stats["novo"],
        delta="",
        delta_color="off"
    )

with col3:
    st.metric(
        "Qualificados",
        stats["qualificado"],
        delta="",
        delta_color="off"
    )

with col4:
    st.metric(
        "Em Atendimento",
        stats["em_atendimento"],
        delta="",
        delta_color="off"
    )

with col5:
    st.metric(
        "Finalizados",
        stats["finalizado"],
        delta="",
        delta_color="off"
    )

st.divider()

# Tabs
tab1, tab2, tab3 = st.tabs([
    "📋 Leads Qualificados",
    "🔍 Todos os Leads",
    "💬 Detalhes do Lead"
])

with tab1:
    st.subheader("Leads Prontos para Atendimento")
    
    db = get_db()
    qualified_leads = db.query(Lead).filter(
        Lead.status == "qualificado"
    ).order_by(Lead.qualified_at.desc()).all()
    db.close()
    
    if not qualified_leads:
        st.info("Nenhum lead qualificado no momento.")
    else:
        for lead in qualified_leads:
            with st.container():
                col1, col2, col3, col4 = st.columns([2, 2, 1, 1])
                
                with col1:
                    st.markdown(f"**{lead.name or 'Sem nome'}**")
                    # Remove o 9 inicial se houver (apenas visual)
                    phone = lead.whatsapp_number
                    if phone and len(phone) >= 11 and phone[2] == '9':
                        phone = phone[:2] + phone[3:]
                    st.caption(f"📱 {phone}")
                
                with col2:
                    st.markdown(f"**Interesse:** {lead.interest or 'N/A'}")
                    st.markdown(f"**Necessidade:** {lead.necessity or 'N/A'}")
                
                with col3:
                    time_diff = datetime.utcnow() - lead.qualified_at
                    if time_diff < timedelta(hours=1):
                        st.caption(f"⏱️ {int(time_diff.total_seconds()/60)}m atrás")
                    else:
                        st.caption(f"⏱️ {time_diff.days}d atrás")
                
                with col4:
                    if st.button("👤 Assumir", key=f"assume_{lead.id}"):
                        db = get_db()
                        LeadService.update_lead(
                            db,
                            lead,
                            status="em_atendimento",
                            attended_by=f"Atendente #{lead.id}"
                        )
                        db.close()
                        st.success("✅ Lead assumido!")
                        refresh_data()
                
                st.divider()

with tab2:
    st.subheader("Todos os Leads")
    
    # Filtros
    col1, col2, col3 = st.columns(3)
    
    with col1:
        filter_status = st.multiselect(
            "Status",
            ["novo", "qualificado", "em_atendimento", "finalizado"],
            default=["novo", "qualificado"]
        )
    
    with col2:
        filter_customer = st.multiselect(
            "Tipo de Cliente",
            ["novo", "existente"],
            default=["novo", "existente"]
        )
    
    with col3:
        sort_by = st.selectbox(
            "Ordenar por",
            ["Data (Recentes)", "Data (Antigos)", "Nome"]
        )
    
    # Query com filtros
    db = get_db()
    query = db.query(Lead)
    
    if filter_status:
        query = query.filter(Lead.status.in_(filter_status))
    
    if filter_customer:
        query = query.filter(Lead.customer_type.in_(filter_customer))
    
    # Ordenação
    if sort_by == "Data (Recentes)":
        query = query.order_by(Lead.created_at.desc())
    elif sort_by == "Data (Antigos)":
        query = query.order_by(Lead.created_at.asc())
    else:
        query = query.order_by(Lead.name.asc())
    
    all_leads = query.all()
    db.close()
    
    # Exibição em tabela
    if all_leads:
        df_data = []
        for lead in all_leads:
            df_data.append({
                "ID": lead.id,
                "Nome": lead.name or "—",
                # Remove o 9 inicial se houver (apenas visual)
                phone = lead.whatsapp_number
                if phone and len(phone) >= 11 and phone[2] == '9':
                    phone = phone[:2] + phone[3:]
                "WhatsApp": phone,
                "Status": lead.status,
                "Tipo": lead.customer_type,
                "IA Ativa": "✅" if lead.status_ia == 1 else "❌",
                "Criado": lead.created_at.strftime("%d/%m %H:%M"),
            })
        
        df = pd.DataFrame(df_data)
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("Nenhum lead encontrado com os filtros selecionados.")

with tab3:
    st.subheader("Histórico Detalhado do Lead")
    
    leads = load_leads()
    
    if not leads:
        st.warning("Nenhum lead registrado ainda.")
    else:
        # Selector de lead
        lead_options = {
            # Remove o 9 inicial se houver (apenas visual)
            phone = lead.whatsapp_number
            if phone and len(phone) >= 11 and phone[2] == '9':
                phone = phone[:2] + phone[3:]
            f"{lead.name or 'Sem nome'} ({phone})": lead.id
            for lead in leads
        }
        
        selected_lead_label = st.selectbox(
            "Selecione um lead",
            options=lead_options.keys()
        )
        
        selected_lead_id = lead_options[selected_lead_label]
        lead, messages = load_lead_details(selected_lead_id)
        
        if lead:
            # Informações do lead
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### 👤 Informações")
                st.markdown(f"**Nome:** {lead.name or 'Não preenchido'}")
                # Remove o 9 inicial se houver (apenas visual)
                phone = lead.whatsapp_number
                if phone and len(phone) >= 11 and phone[2] == '9':
                    phone = phone[:2] + phone[3:]
                st.markdown(f"**WhatsApp:** {phone}")
                st.markdown(f"**Status:** `{lead.status}`")
                st.markdown(f"**Tipo:** {lead.customer_type}")
            
            with col2:
                st.markdown("### 📊 Status da IA")
                st.markdown(f"**IA Ativa:** {'✅ Sim' if lead.status_ia == 1 else '❌ Não'}")
                if lead.attended_by:
                    st.markdown(f"**Atendente:** {lead.attended_by}")
                if lead.qualified_at:
                    st.markdown(f"**Qualificado em:** {lead.qualified_at.strftime('%d/%m/%Y %H:%M')}")
            
            st.divider()
            
            # Informações de qualificação
            st.markdown("### 🎯 Informações de Qualificação")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown(f"**Interesse:**")
                st.info(lead.interest or "Não informado")
            
            with col2:
                st.markdown(f"**Necessidade:**")
                st.info(lead.necessity or "Não informado")
            
            with col3:
                st.markdown(f"**Criado em:**")
                st.info(lead.created_at.strftime("%d/%m/%Y %H:%M"))
            
            st.divider()
            
            # Histórico de mensagens
            st.markdown("### 💬 Histórico de Chat")
            
            if messages:
                for msg in messages:
                    with st.container():
                        if msg.sender == "user":
                            st.markdown(f"**👤 Cliente:** {msg.message}")
                        else:
                            st.markdown(f"**🤖 IA:** {msg.message}")
                        
                        st.caption(f"_{msg.created_at.strftime('%d/%m %H:%M:%S')}_")
                        st.divider()
            else:
                st.info("Nenhuma mensagem registrada ainda.")
            
            # Ações
            st.divider()
            st.markdown("### ⚙️ Ações")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("❌ Desativar IA", key=f"deactivate_{lead.id}"):
                    db = get_db()
                    LeadService.update_lead(db, lead, status_ia=0)
                    db.close()
                    st.success("IA desativada!")
                    refresh_data()
            
            with col2:
                if st.button("✅ Marcar como Finalizado", key=f"finish_{lead.id}"):
                    db = get_db()
                    LeadService.update_lead(db, lead, status="finalizado")
                    db.close()
                    st.success("Lead finalizado!")
                    refresh_data()
            
            with col3:
                if st.button("🔄 Reativar IA", key=f"reactivate_{lead.id}"):
                    db = get_db()
                    LeadService.update_lead(db, lead, status_ia=1)
                    db.close()
                    st.success("IA reativada!")
                    refresh_data()

# Footer
st.divider()
col1, col2, col3 = st.columns(3)

with col1:
    st.caption(f"Última atualização: {datetime.now().strftime('%H:%M:%S')}")

with col2:
    st.caption("CRM System v1.0")

with col3:
    st.caption("Powered by Claude + Evolution API")
