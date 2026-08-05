from contextlib import contextmanager
from datetime import date

import pandas as pd
from sqlalchemy import func

from data_loader import load_workbook_bundle
from database import Session
from models import Brand, CampaignResult, CompositionResult


@contextmanager
def session_scope(session=None):
	db = session or Session()
	own_session = session is None
	try:
		yield db
		if own_session:
			db.commit()
	except Exception:
		if own_session:
			db.rollback()
		raise
	finally:
		if own_session:
			db.close()


def list_brands(session=None):
	with session_scope(session) as db:
		names = [row[0] for row in db.query(Brand.name).order_by(Brand.name.asc()).all()]
	return names or ["Unilever"]


def list_brand_months(brand_name, session=None):
	with session_scope(session) as db:
		months = (
			db.query(CampaignResult.report_month)
			.filter(func.lower(CampaignResult.brand_name) == brand_name.lower())
			.distinct()
			.order_by(CampaignResult.report_month.desc())
			.all()
		)
	return [row[0] for row in months]


def _month_floor(value):
	if value is None:
		return None
	return date(value.year, value.month, 1)


def _resolve_safra_window(session=None, brand_name=None, safra_end_month=None):
	if safra_end_month is not None:
		end_month = _month_floor(safra_end_month)
	else:
		with session_scope(session) as db:
			query = db.query(func.max(CampaignResult.report_month))
			if brand_name and brand_name != "Todas as marcas":
				query = query.filter(
					func.lower(CampaignResult.brand_name) == brand_name.lower()
				)
			end_month = query.scalar()
			end_month = _month_floor(end_month)

	if end_month is None:
		return None, None

	start_month = (pd.Timestamp(end_month) - pd.DateOffset(months=11)).date()
	start_month = date(start_month.year, start_month.month, 1)
	return start_month, end_month


def create_brand(name, session=None):
	clean_name = name.strip()
	if not clean_name:
		return False

	with session_scope(session) as db:
		existing = (
			db.query(Brand)
			.filter(func.lower(Brand.name) == clean_name.lower())
			.first()
		)
		if existing is None:
			db.add(Brand(name=clean_name))
			return True
	return False


def delete_brand(name, session=None):
	with session_scope(session) as db:
		brand = (
			db.query(Brand)
			.filter(func.lower(Brand.name) == name.lower())
			.first()
		)
		if brand is None:
			return False

		db.query(CampaignResult).filter(
			func.lower(CampaignResult.brand_name) == name.lower()
		).delete(synchronize_session=False)
		db.query(CompositionResult).filter(
			func.lower(CompositionResult.brand_name) == name.lower()
		).delete(synchronize_session=False)
		db.delete(brand)
		return True


def sync_workbook(uploaded_file, brand_name, session=None):
	bundle = load_workbook_bundle(uploaded_file)
	df_resultados = bundle["df_resultados"]
	df_recomposicao = bundle["df_recomposicao"]
	report_month = bundle["report_month"]
	clean_brand = (brand_name or "Unilever").strip() or "Unilever"

	with session_scope(session) as db:
		create_brand(clean_brand, session=db)

		db.query(CampaignResult).filter(
			func.lower(CampaignResult.brand_name) == clean_brand.lower()
			,
			CampaignResult.report_month == report_month,
		).delete(synchronize_session=False)
		db.query(CompositionResult).filter(
			func.lower(CompositionResult.brand_name) == clean_brand.lower()
			,
			CompositionResult.report_month == report_month,
		).delete(synchronize_session=False)

		for row in df_resultados.to_dict("records"):
			db.add(
				CampaignResult(
					brand_name=clean_brand,
					report_month=report_month,
					campaign=str(row.get("Campanha", "")),
					qtd_venda=int(row.get("Qtd Venda", 0) or 0),
					disparados=int(row.get("Disparados", 0) or 0),
					entregues=int(row.get("Entregues", 0) or 0),
					taxa_entrega=float(row.get("Taxa de Entrega", 0) or 0),
					aberturas=int(row.get("Aberturas", 0) or 0),
					cliques=int(row.get("Cliques", 0) or 0),
					clientes=int(row.get("Clientes", 0) or 0),
					receita=float(row.get("Receita", 0) or 0),
					desconto=float(row.get("Desconto", 0) or 0),
				)
			)

		for row in df_recomposicao.to_dict("records"):
			db.add(
				CompositionResult(
					brand_name=clean_brand,
					report_month=report_month,
					categoria=str(row.get("Categoria", "")),
					comprador=str(row.get("Comprador", "")),
					contato=str(row.get("Contato", "")),
					receita=float(row.get("Receita", 0) or 0),
					desconto=float(row.get("Desconto", 0) or 0),
					taxa_desconto=float(row.get("Taxa de Desconto", 0) or 0),
					participacao_receita=float(
						row.get("Participação na Receita", 0) or 0
					),
				)
			)

		return {
			"brand_name": clean_brand,
			"report_month": report_month,
			"campaign_rows": len(df_resultados),
			"composition_rows": len(df_recomposicao),
		}


def _query_campaigns(session=None, brand_name=None, start_month=None, end_month=None):
	with session_scope(session) as db:
		query = db.query(CampaignResult)
		if brand_name and brand_name != "Todas as marcas":
			query = query.filter(
				func.lower(CampaignResult.brand_name) == brand_name.lower()
			)
		if start_month is not None:
			query = query.filter(CampaignResult.report_month >= start_month)
		if end_month is not None:
			query = query.filter(CampaignResult.report_month <= end_month)

		rows = query.order_by(CampaignResult.receita.desc()).all()

	return pd.DataFrame(
		[
			{
				"Marca": row.brand_name,
				"report_month": row.report_month,
				"Campanha": row.campaign,
				"Qtd Venda": row.qtd_venda,
				"Disparados": row.disparados,
				"Entregues": row.entregues,
				"Taxa de Entrega": row.taxa_entrega,
				"Aberturas": row.aberturas,
				"Cliques": row.cliques,
				"Clientes": row.clientes,
				"Receita": row.receita,
				"Desconto": row.desconto,
			}
			for row in rows
		]
	)


def _query_composition(session=None, brand_name=None, start_month=None, end_month=None):
	with session_scope(session) as db:
		query = db.query(CompositionResult)
		if brand_name and brand_name != "Todas as marcas":
			query = query.filter(
				func.lower(CompositionResult.brand_name) == brand_name.lower()
			)
		if start_month is not None:
			query = query.filter(CompositionResult.report_month >= start_month)
		if end_month is not None:
			query = query.filter(CompositionResult.report_month <= end_month)

		rows = query.order_by(CompositionResult.receita.desc()).all()

	return pd.DataFrame(
		[
			{
				"Marca": row.brand_name,
				"report_month": row.report_month,
				"Categoria": row.categoria,
				"Comprador": row.comprador,
				"Contato": row.contato,
				"Receita": row.receita,
				"Desconto": row.desconto,
				"Taxa de Desconto": row.taxa_desconto,
				"Participação na Receita": row.participacao_receita,
			}
			for row in rows
		]
	)


def _monthly_series(df):
	if df.empty:
		return pd.DataFrame(columns=["report_month", "Receita", "Desconto", "Clientes", "Campanhas"])

	if "report_month" not in df.columns:
		return pd.DataFrame(columns=["report_month", "Receita", "Desconto", "Clientes", "Campanhas"])

	return (
		df.groupby("report_month", as_index=False)
		.agg(
			Receita=("Receita", "sum"),
			Desconto=("Desconto", "sum"),
			Clientes=("Clientes", "sum"),
			Campanhas=("Campanha", "count"),
		)
		.sort_values("report_month")
	)


	return {
		"start_month": start_month,
		"end_month": end_month,
	}


def load_dashboard_data(session=None, brand_name=None, safra_end_month=None):
	start_month, end_month = _resolve_safra_window(
		session=session,
		brand_name=brand_name,
		safra_end_month=safra_end_month,
	)
	brand_df = _query_campaigns(
		session=session,
		brand_name=brand_name,
		start_month=start_month,
		end_month=end_month,
	)
	brand_comp = _query_composition(
		session=session,
		brand_name=brand_name,
		start_month=start_month,
		end_month=end_month,
	)
	geral_df = _query_campaigns(
		session=session,
		brand_name=None,
		start_month=start_month,
		end_month=end_month,
	)
	geral_comp = _query_composition(
		session=session,
		brand_name=None,
		start_month=start_month,
		end_month=end_month,
	)

	total_receita = float(brand_df["Receita"].sum()) if not brand_df.empty else 0.0
	total_desconto = float(brand_df["Desconto"].sum()) if not brand_df.empty else 0.0
	total_clientes = int(brand_df["Clientes"].sum()) if not brand_df.empty else 0
	total_disparados = int(brand_df["Disparados"].sum()) if not brand_df.empty else 0
	total_entregues = int(brand_df["Entregues"].sum()) if not brand_df.empty else 0
	total_aberturas = int(brand_df["Aberturas"].sum()) if not brand_df.empty else 0
	total_cliques = int(brand_df["Cliques"].sum()) if not brand_df.empty else 0
	total_receita_geral = float(geral_df["Receita"].sum()) if not geral_df.empty else 0.0
	total_desconto_geral = float(geral_df["Desconto"].sum()) if not geral_df.empty else 0.0
	roi = (total_receita / total_desconto) if total_desconto else 0.0
	taxa_abertura = (total_aberturas / total_entregues) if total_entregues else 0.0
	taxa_clique = (total_cliques / total_disparados) if total_disparados else 0.0
	share_faturamento = (
		(total_receita / total_receita_geral) if total_receita_geral else 0.0
	)
	recorrente_pct = min(100.0, max(0.0, taxa_abertura * 100))
	serie_brand = _monthly_series(brand_df)
	serie_geral = _monthly_series(geral_df)

	return {
		"df_resultados": brand_df,
		"df_composicao": brand_comp,
		"df_resultados_geral": geral_df,
		"df_composicao_geral": geral_comp,
		"serie_mensal": serie_brand,
		"serie_mensal_geral": serie_geral,
		"safra_start": start_month,
		"safra_end": end_month,
		"metrics": {
			"receita_total": total_receita,
			"share_faturamento": share_faturamento,
			"desconto_total": total_desconto,
			"desconto_total_geral": total_desconto_geral,
			"receita_total_geral": total_receita_geral,
			"roi": roi,
			"base_unica": total_clientes,
			"taxa_abertura": taxa_abertura,
			"taxa_clique": taxa_clique,
			"entregues": total_entregues,
			"disparados": total_disparados,
			"recorrente_pct": recorrente_pct,
		},
	}