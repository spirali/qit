#ifndef QIT_TAKE_H

#include <stdlib.h>

namespace qit {

template<typename Tin, typename Tout, typename F> class MapIterator {
	public:
		typedef Tout value_type;
		MapIterator(Tin &iterator) : iterator(iterator) {}

		bool next(value_type &out) {
			typename Tin::value_type v;
			if (!iterator.next(v)) {
				return false;
			}
			F f;
			out = f(v);
			return true;
		}

		void reset() {
			iterator.reset();
		}
	protected:
		Tin &iterator;
		int count;
};

}

#endif // QIT_TAKE_H
