from __future__ import annotations

import pandas as pd
import streamlit as st
from sqlalchemy import select

if __package__:
    from .database import SessionLocal, get_database_url, init_db
    from .models import DonatedSupply, FoodItem, Supplier, Worker
else:
    from database import SessionLocal, get_database_url, init_db
    from models import DonatedSupply, FoodItem, Supplier, Worker

init_db()


st.set_page_config(
    page_title="Festa IFC",
    page_icon="🎉",
    layout="wide",
)


def get_all_items(model):
    with SessionLocal() as session:
        return session.execute(select(model)).scalars().all()


def render_dashboard():
    st.title("Sistema de organização da festa do IFC Campus Blumenau")
    st.caption(f"Banco ativo: {get_database_url()}")

    with SessionLocal() as session:
        total_food = session.execute(select(FoodItem)).scalars().all()
        total_suppliers = session.execute(select(Supplier)).scalars().all()
        total_workers = session.execute(select(Worker)).scalars().all()
        total_supplies = session.execute(select(DonatedSupply)).scalars().all()

    columns = st.columns(4)
    columns[0].metric("Alimentos", len(total_food))
    columns[1].metric("Fornecedores", len(total_suppliers))
    columns[2].metric("Pessoas", len(total_workers))
    columns[3].metric("Insumos doados", len(total_supplies))

    st.subheader("Resumo da festa")
    if total_food:
        food_data = pd.DataFrame(
            [
                {
                    "Alimento": item.name,
                    "Categoria": item.category,
                    "Estoque": item.stock,
                    "Preço de venda": f"R$ {item.sale_price:.2f}",
                }
                for item in total_food
            ]
        )
        st.dataframe(food_data, use_container_width=True)
    else:
        st.info("Nenhum alimento cadastrado ainda.")

    st.subheader("Distribuição das pessoas")
    if total_workers:
        worker_groups = {}
        for worker in total_workers:
            worker_groups[worker.group_type] = worker_groups.get(worker.group_type, 0) + 1
        st.bar_chart(pd.DataFrame({"Pessoas": list(worker_groups.values())}, index=list(worker_groups.keys())))
    else:
        st.info("Nenhuma pessoa cadastrada ainda.")


def render_food_page():
    st.header("CRUD de alimentos")
    with SessionLocal() as session:
        suppliers = session.execute(select(Supplier)).scalars().all()
        items = session.execute(select(FoodItem)).scalars().all()

    supplier_ids = [supplier.id for supplier in suppliers]
    supplier_lookup = {supplier.id: supplier.name for supplier in suppliers}

    selected_item_label = st.selectbox(
        "Editar um item existente",
        ["Novo item"] + [f"{item.id} - {item.name}" for item in items],
        index=0,
    )

    selected_item = None
    if selected_item_label != "Novo item":
        selected_id = int(selected_item_label.split(" - ")[0])
        with SessionLocal() as session:
            selected_item = session.get(FoodItem, selected_id)

    defaults = {
        "name": selected_item.name if selected_item else "",
        "category": selected_item.category if selected_item else "",
        "stock": int(selected_item.stock) if selected_item else 0,
        "sale_price": float(selected_item.sale_price) if selected_item else 0.0,
        "description": selected_item.description if selected_item else "",
        "supplier_id": selected_item.supplier_id if selected_item else None,
    }

    with st.form("food_form", clear_on_submit=True):
        name = st.text_input("Nome do alimento", value=defaults["name"])
        category = st.text_input("Categoria", value=defaults["category"])
        stock = st.number_input("Quantidade em estoque", min_value=0, value=defaults["stock"])
        sale_price = st.number_input("Preço de venda (R$)", min_value=0.0, value=float(defaults["sale_price"]))
        description = st.text_area("Descrição", value=defaults["description"], height=120)
        supplier_id = st.selectbox(
            "Fornecedor",
            options=[None] + supplier_ids,
            format_func=lambda option: "Sem fornecedor" if option is None else supplier_lookup.get(option, "Fornecedor"),
            index=(supplier_ids.index(defaults["supplier_id"]) + 1) if defaults["supplier_id"] in supplier_ids else 0,
        )

        submitted = st.form_submit_button("Salvar alimento")
        if submitted:
            with SessionLocal() as session:
                if selected_item is not None:
                    selected_item.name = name
                    selected_item.category = category
                    selected_item.stock = stock
                    selected_item.sale_price = sale_price
                    selected_item.description = description
                    selected_item.supplier_id = supplier_id
                    st.success("Alimento atualizado com sucesso!")
                else:
                    session.add(
                        FoodItem(
                            name=name,
                            category=category,
                            stock=stock,
                            sale_price=sale_price,
                            description=description,
                            supplier_id=supplier_id,
                        )
                    )
                    st.success("Alimento cadastrado com sucesso!")
                session.commit()
            st.rerun()

    st.subheader("Lista de alimentos")
    with SessionLocal() as session:
        foods = session.execute(select(FoodItem)).scalars().all()

    if foods:
        table = pd.DataFrame(
            [
                {
                    "ID": item.id,
                    "Nome": item.name,
                    "Categoria": item.category,
                    "Estoque": item.stock,
                    "Preço": f"R$ {item.sale_price:.2f}",
                    "Fornecedor": item.supplier.name if item.supplier else "Sem fornecedor",
                }
                for item in foods
            ]
        )
        st.dataframe(table, use_container_width=True)

        for item in foods:
            if st.button(f"Excluir alimento #{item.id}", key=f"delete_food_{item.id}"):
                with SessionLocal() as session:
                    entity = session.get(FoodItem, item.id)
                    if entity:
                        session.delete(entity)
                        session.commit()
                st.rerun()
    else:
        st.info("Nenhum alimento cadastrado.")


def render_supplier_page():
    st.header("CRUD de fornecedores")
    with SessionLocal() as session:
        suppliers = session.execute(select(Supplier)).scalars().all()

    selected_label = st.selectbox(
        "Editar um fornecedor existente",
        ["Novo fornecedor"] + [f"{supplier.id} - {supplier.name}" for supplier in suppliers],
        index=0,
    )

    selected_supplier = None
    if selected_label != "Novo fornecedor":
        selected_id = int(selected_label.split(" - ")[0])
        with SessionLocal() as session:
            selected_supplier = session.get(Supplier, selected_id)

    defaults = {
        "name": selected_supplier.name if selected_supplier else "",
        "contact": selected_supplier.contact if selected_supplier else "",
        "support_type": selected_supplier.support_type if selected_supplier else "",
        "notes": selected_supplier.notes if selected_supplier else "",
    }

    with st.form("supplier_form", clear_on_submit=True):
        name = st.text_input("Nome do fornecedor", value=defaults["name"])
        contact = st.text_input("Contato", value=defaults["contact"])
        support_type = st.text_input("Tipo de apoio", value=defaults["support_type"])
        notes = st.text_area("Observações", value=defaults["notes"], height=120)

        submitted = st.form_submit_button("Salvar fornecedor")
        if submitted:
            with SessionLocal() as session:
                if selected_supplier is not None:
                    selected_supplier.name = name
                    selected_supplier.contact = contact
                    selected_supplier.support_type = support_type
                    selected_supplier.notes = notes
                    st.success("Fornecedor atualizado com sucesso!")
                else:
                    session.add(
                        Supplier(
                            name=name,
                            contact=contact,
                            support_type=support_type,
                            notes=notes,
                        )
                    )
                    st.success("Fornecedor cadastrado com sucesso!")
                session.commit()
            st.rerun()

    st.subheader("Lista de fornecedores")
    with SessionLocal() as session:
        suppliers = session.execute(select(Supplier)).scalars().all()
    if suppliers:
        table = pd.DataFrame(
            [
                {
                    "ID": supplier.id,
                    "Nome": supplier.name,
                    "Contato": supplier.contact,
                    "Tipo de apoio": supplier.support_type,
                    "Observações": supplier.notes,
                }
                for supplier in suppliers
            ]
        )
        st.dataframe(table, use_container_width=True)

        for supplier in suppliers:
            if st.button(f"Excluir fornecedor #{supplier.id}", key=f"delete_supplier_{supplier.id}"):
                with SessionLocal() as session:
                    entity = session.get(Supplier, supplier.id)
                    if entity:
                        session.delete(entity)
                        session.commit()
                st.rerun()
    else:
        st.info("Nenhum fornecedor cadastrado.")


def render_worker_page():
    st.header("CRUD de pessoas envolvidas")
    with SessionLocal() as session:
        workers = session.execute(select(Worker)).scalars().all()

    selected_label = st.selectbox(
        "Editar uma pessoa existente",
        ["Nova pessoa"] + [f"{worker.id} - {worker.name}" for worker in workers],
        index=0,
    )

    selected_worker = None
    if selected_label != "Nova pessoa":
        selected_id = int(selected_label.split(" - ")[0])
        with SessionLocal() as session:
            selected_worker = session.get(Worker, selected_id)

    defaults = {
        "name": selected_worker.name if selected_worker else "",
        "group_type": selected_worker.group_type if selected_worker else "",
        "role": selected_worker.role if selected_worker else "",
        "phone": selected_worker.phone if selected_worker else "",
        "notes": selected_worker.notes if selected_worker else "",
    }

    with st.form("worker_form", clear_on_submit=True):
        name = st.text_input("Nome", value=defaults["name"])
        group_type = st.selectbox(
            "Categoria",
            ["Aluno", "Pai de aluno", "Servidor"],
            index=["Aluno", "Pai de aluno", "Servidor"].index(defaults["group_type"]) if defaults["group_type"] in ["Aluno", "Pai de aluno", "Servidor"] else 0,
        )
        role = st.text_input("Função", value=defaults["role"])
        phone = st.text_input("Telefone", value=defaults["phone"])
        notes = st.text_area("Observações", value=defaults["notes"], height=110)

        submitted = st.form_submit_button("Salvar pessoa")
        if submitted:
            with SessionLocal() as session:
                if selected_worker is not None:
                    selected_worker.name = name
                    selected_worker.group_type = group_type
                    selected_worker.role = role
                    selected_worker.phone = phone
                    selected_worker.notes = notes
                    st.success("Pessoa atualizada com sucesso!")
                else:
                    session.add(
                        Worker(
                            name=name,
                            group_type=group_type,
                            role=role,
                            phone=phone,
                            notes=notes,
                        )
                    )
                    st.success("Pessoa cadastrada com sucesso!")
                session.commit()
            st.rerun()

    st.subheader("Lista de pessoas")
    with SessionLocal() as session:
        workers = session.execute(select(Worker)).scalars().all()
    if workers:
        table = pd.DataFrame(
            [
                {
                    "ID": worker.id,
                    "Nome": worker.name,
                    "Categoria": worker.group_type,
                    "Função": worker.role,
                    "Telefone": worker.phone,
                    "Observações": worker.notes,
                }
                for worker in workers
            ]
        )
        st.dataframe(table, use_container_width=True)

        for worker in workers:
            if st.button(f"Excluir pessoa #{worker.id}", key=f"delete_worker_{worker.id}"):
                with SessionLocal() as session:
                    entity = session.get(Worker, worker.id)
                    if entity:
                        session.delete(entity)
                        session.commit()
                st.rerun()
    else:
        st.info("Nenhuma pessoa cadastrada.")


def render_supply_page():
    st.header("CRUD de insumos doados")
    with SessionLocal() as session:
        suppliers = session.execute(select(Supplier)).scalars().all()
        supplies = session.execute(select(DonatedSupply)).scalars().all()

    supplier_ids = [supplier.id for supplier in suppliers]
    supplier_lookup = {supplier.id: supplier.name for supplier in suppliers}

    selected_label = st.selectbox(
        "Editar um insumo existente",
        ["Novo insumo"] + [f"{supply.id} - {supply.name}" for supply in supplies],
        index=0,
    )

    selected_supply = None
    if selected_label != "Novo insumo":
        selected_id = int(selected_label.split(" - ")[0])
        with SessionLocal() as session:
            selected_supply = session.get(DonatedSupply, selected_id)

    defaults = {
        "name": selected_supply.name if selected_supply else "",
        "quantity": int(selected_supply.quantity) if selected_supply else 0,
        "unit": selected_supply.unit if selected_supply else "unidade",
        "description": selected_supply.description if selected_supply else "",
        "supplier_id": selected_supply.supplier_id if selected_supply else None,
    }

    with st.form("supply_form", clear_on_submit=True):
        name = st.text_input("Nome do insumo", value=defaults["name"])
        quantity = st.number_input("Quantidade", min_value=0, value=defaults["quantity"])
        unit = st.text_input("Unidade", value=defaults["unit"])
        description = st.text_area("Descrição", value=defaults["description"], height=120)
        supplier_id = st.selectbox(
            "Fornecedor doador",
            options=[None] + supplier_ids,
            format_func=lambda option: "Sem fornecedor" if option is None else supplier_lookup.get(option, "Fornecedor"),
            index=(supplier_ids.index(defaults["supplier_id"]) + 1) if defaults["supplier_id"] in supplier_ids else 0,
        )

        submitted = st.form_submit_button("Salvar insumo")
        if submitted:
            with SessionLocal() as session:
                if selected_supply is not None:
                    selected_supply.name = name
                    selected_supply.quantity = quantity
                    selected_supply.unit = unit
                    selected_supply.description = description
                    selected_supply.supplier_id = supplier_id
                    st.success("Insumo atualizado com sucesso!")
                else:
                    session.add(
                        DonatedSupply(
                            name=name,
                            quantity=quantity,
                            unit=unit,
                            description=description,
                            supplier_id=supplier_id,
                        )
                    )
                    st.success("Insumo cadastrado com sucesso!")
                session.commit()
            st.rerun()

    st.subheader("Lista de insumos doados")
    with SessionLocal() as session:
        supplies = session.execute(select(DonatedSupply)).scalars().all()
    if supplies:
        table = pd.DataFrame(
            [
                {
                    "ID": supply.id,
                    "Nome": supply.name,
                    "Quantidade": supply.quantity,
                    "Unidade": supply.unit,
                    "Fornecedor": supply.supplier.name if supply.supplier else "Sem fornecedor",
                    "Descrição": supply.description,
                }
                for supply in supplies
            ]
        )
        st.dataframe(table, use_container_width=True)

        for supply in supplies:
            if st.button(f"Excluir insumo #{supply.id}", key=f"delete_supply_{supply.id}"):
                with SessionLocal() as session:
                    entity = session.get(DonatedSupply, supply.id)
                    if entity:
                        session.delete(entity)
                        session.commit()
                st.rerun()
    else:
        st.info("Nenhum insumo cadastrado.")


def main():
    page = st.sidebar.radio(
        "Navegação",
        ["Dashboard", "Alimentos", "Fornecedores", "Insumos", "Pessoas"],
    )

    if page == "Dashboard":
        render_dashboard()
    elif page == "Alimentos":
        render_food_page()
    elif page == "Fornecedores":
        render_supplier_page()
    elif page == "Insumos":
        render_supply_page()
    elif page == "Pessoas":
        render_worker_page()


if __name__ == "__main__":
    main()
