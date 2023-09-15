from typing import Dict

from cruds.core import Connectable
from models.cmdb import (
    IdentityProviderQuery,
    IdentityProviderRead,
    IdentityProviderWrite,
    ProviderRead,
)
from pydantic import AnyHttpUrl


class IdentityProviderCRUD(
    Connectable[IdentityProviderWrite, IdentityProviderRead, IdentityProviderQuery]
):
    def __init__(
        self,
        get_url: AnyHttpUrl,
        post_url: AnyHttpUrl,
        patch_url: AnyHttpUrl,
        connect_url: AnyHttpUrl,
        read_headers: Dict[str, str],
        write_headers: Dict[str, str],
    ) -> None:
        super().__init__(
            type="IdentityProvider",
            read_schema=IdentityProviderRead,
            write_schema=IdentityProviderWrite,
            get_url=get_url,
            post_url=post_url,
            patch_url=patch_url,
            connect_url=connect_url,
            read_headers=read_headers,
            write_headers=write_headers,
        )

    def create_or_update(
        self, *, item: IdentityProviderWrite, parent: ProviderRead
    ) -> IdentityProviderRead:
        db_item = self.single(data=IdentityProviderQuery(endpoint=item.endpoint))
        db_item = super().create_or_update(item=item, db_item=db_item)
        self.connect(new_data=item, uid=db_item.uid, parent_uid=parent.uid)
        return db_item